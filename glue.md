# Guia Geral do Projeto Glue Job

## Objetivo

Este documento descreve a arquitetura, a organização do código, o fluxo de execução, a estratégia de execução local com Docker + LocalStack e o passo a passo para rodar e debugar a aplicação no PyCharm.

O objetivo é permitir que outros times consigam:

- entender rapidamente como o projeto foi estruturado;
- manter o fluxo atual com segurança;
- evoluir a solução para novas tabelas do DynamoDB;
- executar e depurar a aplicação localmente sem rodar o job dentro do container.

---

## Visão Geral

O projeto implementa um Glue Job com o fluxo:

```text
DynamoDB
   |
   | leitura full ou incremental
   v
Glue Job / PySpark
   |
   | padronização + partição ano_mes_dia
   v
Data Mesh
   |
   | atualiza data de corte apenas em sucesso
   v
SSM Parameter Store
```

No estado atual do projeto:

- a origem é uma tabela do DynamoDB;
- a data de corte é armazenada no SSM Parameter Store;
- a escrita oficial de produção é feita via `saveAsTable()` no Glue Catalog;
- a escrita local é mantida como dataset Parquet particionado para debug e testes;
- o ambiente local é simulado com LocalStack;
- a execução do job pode ocorrer tanto em container quanto localmente na máquina do desenvolvedor.

---

## Regras de Negócio

### Data de corte

A data de corte é armazenada no Parameter Store no formato `YYYYMMDD`.

Exemplos:

- `20260618`
- `20260619`

Regras:

- se o parâmetro estiver ausente, nulo, vazio ou não puder ser lido, a carga deve ser `FULL`;
- se o parâmetro tiver valor válido, a carga deve ser `INCREMENTAL`;
- ao final de uma execução com sucesso, a data atual da execução deve sobrescrever o parâmetro;
- em caso de erro, o parâmetro não deve ser atualizado.

### Full x Incremental

No estado atual da implementação:

- `FULL`: `scan` completo na tabela do DynamoDB;
- `INCREMENTAL`: `Query + GSI` quando disponível, com fallback para `scan` filtrado.

Observação importante:

- por configuração, o projeto pode permanecer em `FULL Scan`;
- quando o incremental é habilitado, o reader tenta `Query + GSI` e faz fallback sem quebrar o fluxo.

### Campo `startAt`

O campo `startAt` é do tipo `string`. Isso funciona corretamente para comparações de corte desde que o valor permaneça sempre no formato `YYYYMMDD`.

Exemplos válidos:

- `20260618`
- `20260701`

Esse formato preserva a ordenação cronológica na comparação textual da string.

---

## Estrutura do Projeto

```text
glue/
├── docker/
│   └── localstack/
│       └── init/
│           └── ready.d/
├── src/
│   ├── config/
│   ├── constants/
│   ├── documento/
│   ├── jobs/
│   ├── readers/
│   ├── services/
│   ├── utils/
│   └── writers/
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── glue.md
├── README.md
└── requirements.txt
```

---

## Arquitetura por Camadas

### `config`

Responsável por configuração de ambiente, resolução de argumentos e criação do contexto de execução.

Arquivos principais:

- `src/config/args_resolver.py`
- `src/config/settings.py`
- `src/config/glue_context_factory.py`
- `src/config/spark_config.py`

### `constants`

Responsável por constantes do domínio atual.

Arquivos principais:

- `src/constants/dynamodb.py`
- `src/constants/tables.py`
- `src/constants/parameters.py`

### `jobs`

Camada de entrada e orquestração.

Arquivos principais:

- `src/jobs/tailor_proposal_job.py`
- `src/jobs/job_runner.py`
- `src/jobs/localstack_bootstrap.py`

### `readers`

Camada de leitura da origem.

Arquivo principal:

- `src/readers/dynamodb_reader.py`

### `services`

Camada de apoio ao fluxo e transformação.

Arquivos principais:

- `src/services/parameter_store_service.py`
- `src/services/execution_date_service.py`
- `src/services/dataframe_service.py`

### `writers`

Camada de persistência do destino.

Arquivo principal:

- `src/writers/mesh_writer.py`

### `utils`

Funções compartilhadas e sem regra de negócio principal.

Arquivos principais:

- `src/utils/dates.py`
- `src/utils/logger.py`
- `src/utils/validations.py`

---

## Papel de Cada Classe e Módulo

### `src/jobs/tailor_proposal_job.py`

Ponto de entrada do job.

Responsabilidades:

- resolver argumentos do job;
- construir `Settings`;
- inicializar Spark e contexto Glue/local;
- instanciar dependências;
- montar `JobRunner`;
- iniciar a execução.

Essa classe não deve conter regra de negócio. Ela apenas conecta os componentes.

### `src/jobs/job_runner.py`

Orquestrador central do fluxo.

Responsabilidades:

- ler a última data de execução do SSM;
- decidir entre modo `FULL` e `INCREMENTAL`;
- chamar o `DynamoDBReader`;
- aplicar transformações no DataFrame;
- adicionar a coluna de partição `ano_mes_dia`;
- escrever no destino com `MeshWriter`;
- atualizar o Parameter Store ao final;
- executar `job.commit()` quando houver Glue real;
- registrar logs de início, fim e quantidade de registros.

Classes importantes dentro desse arquivo:

- `CommitableJob`: protocolo simples para abstrair `commit`;
- `JobDependencies`: dataclass que agrupa dependências;
- `JobRunner`: coordena o fluxo do começo ao fim.

### `src/jobs/localstack_bootstrap.py`

Script de inicialização do ambiente local.

Responsabilidades:

- criar a tabela do DynamoDB caso ela não exista;
- criar o parâmetro do SSM caso ele não exista;
- popular a tabela com registros de exemplo.

Esse módulo existe para facilitar testes locais e onboarding.

Detalhes relevantes:

- a tabela é criada com `PK=staticPartitionKey` e `SK=proposalID`;
- o GSI `gsi_startAt` já é criado no ambiente local;
- o parâmetro SSM é criado com valor `" "` porque o SSM não aceita string vazia.

### `src/readers/dynamodb_reader.py`

Responsável pela leitura no DynamoDB.

Responsabilidades:

- criar o client `boto3` do DynamoDB;
- fazer leitura full via `scan`;
- validar se o GSI configurado existe e está `ACTIVE`;
- fazer leitura incremental via `Query + GSI` quando possível;
- fazer fallback para `scan` filtrado quando o GSI não estiver disponível;
- tratar paginação do DynamoDB com `LastEvaluatedKey`;
- desserializar o payload nativo do DynamoDB em tipos Python;
- converter o resultado final em `Spark DataFrame`.

Métodos principais:

- `read_as_dataframe()`: interface principal do reader;
- `_scan_items()`: executa as leituras paginadas;
- `_deserialize_items()`: converte o formato do DynamoDB para Python.

Observação arquitetural:

- a tabela é configurada no construtor do reader;
- o incremental pode ser ativado ou desativado por configuração;
- a regra de comparação da data de corte também é configurável.

### `src/writers/mesh_writer.py`

Responsável pela escrita no destino.

Responsabilidades:

- garantir a ordem final das colunas;
- aplicar particionamento;
- escrever via `saveAsTable()` no Glue Catalog no modo `catalog`;
- escrever em Parquet no filesystem no modo `local`.

Importante:

- `catalog` é o modo oficial de produção;
- `local` existe para debug, testes e validação do fluxo fora da AWS.

### `src/config/args_resolver.py`

Responsável por resolver os parâmetros do job.

Prioridade atual:

1. tentar usar `getResolvedOptions` quando estiver em ambiente Glue;
2. se não existir Glue library, usar variáveis de ambiente;
3. carregar automaticamente `.env` e `.env.local` quando presentes.

Esse módulo é o principal habilitador da execução local fora do container.

### `src/config/settings.py`

Dataclass que centraliza os parâmetros do job.

Responsabilidades:

- armazenar os parâmetros necessários;
- padronizar a construção das configurações a partir dos argumentos.

### `src/config/glue_context_factory.py`

Factory do contexto de execução.

Responsabilidades:

- criar `SparkSession`;
- criar `GlueContext` e `Job` quando a library `awsglue` estiver disponível;
- criar um `LocalJob` quando a execução for local.

Essa abstração evita que o entrypoint precise ter `if/else` de Glue vs local.

### `src/config/spark_config.py`

Responsável por criar a `SparkSession` com as configurações padrão do projeto.

Exemplos de configuração:

- `enableHiveSupport()`
- dynamic partition
- configurações de parquet

### `src/services/parameter_store_service.py`

Wrapper simples para leitura e atualização do SSM Parameter Store.

Responsabilidades:

- ler parâmetro;
- retornar `None` quando não existir;
- atualizar parâmetro no fim do fluxo.

### `src/services/execution_date_service.py`

Responsável pela decisão de carga full ou incremental.

Responsabilidades:

- determinar se uma data recebida representa execução full;
- devolver `None` para full;
- devolver a data válida para o reader no fluxo incremental.

### `src/services/dataframe_service.py`

Responsável por transformações reutilizáveis de DataFrame.

Responsabilidades:

- renomear colunas;
- selecionar colunas na ordem desejada;
- adicionar a coluna `ano_mes_dia`.

### `src/constants/dynamodb.py`

Centraliza:

- lista de colunas esperadas na origem;
- mapa de rename;
- lista final de colunas após renomeação.

Detalhe importante:

- o campo `#st` é renomeado para `st` para evitar problemas em processamento e seleção.

### `src/constants/tables.py`

Centraliza:

- nome do database de destino;
- nome da tabela lógica de destino;
- partições.

### `src/constants/parameters.py`

Centraliza o nome padrão do parâmetro de execução.

### `src/utils/dates.py`

Responsável por manipulação de datas do job.

Hoje fornece:

- a data atual no formato `YYYYMMDD`;
- parser de datas.

### `src/utils/logger.py`

Responsável por criar um logger padronizado do projeto.

### `src/utils/validations.py`

Responsável por validações utilitárias simples.

Hoje o método principal é `is_blank()`, usado na decisão de full/incremental.

---

## Fluxo de Execução do Job

```text
tailor_proposal_job.main()
    |
    +-- resolve_job_args()
    |
    +-- Settings.from_args()
    |
    +-- GlueContextFactory.create()
    |
    +-- cria serviços e readers/writers
    |
    +-- JobRunner.execute()
            |
            +-- lê SSM Parameter Store
            +-- decide FULL ou INCREMENTAL
            +-- lê DynamoDB
            +-- renomeia e seleciona colunas
            +-- adiciona ano_mes_dia
            +-- escreve Parquet
            +-- atualiza parâmetro SSM
            +-- commit do job
```

---

## Arquitetura do Docker

### Objetivo

O Docker neste projeto não é obrigatório para executar o código, mas é a base do ambiente local para simular os serviços AWS com LocalStack.

### Serviços definidos no `docker-compose.yml`

#### `localstack`

Responsável por simular serviços AWS localmente.

Serviços habilitados:

- `dynamodb`
- `ssm`
- `s3`

Porta exposta:

- `4566`

#### `bootstrap`

Container auxiliar que roda uma vez para preparar o ambiente.

Responsabilidades:

- garantir a existência da tabela do DynamoDB;
- garantir a existência do parâmetro SSM;
- inserir registros de exemplo.

Esse serviço chama:

```bash
python -m jobs.localstack_bootstrap
```

#### `app`

Container da aplicação.

Responsável por executar o job dentro do Docker quando desejado.

Esse serviço chama:

```bash
python -m jobs.tailor_proposal_job
```

### Como os serviços se enxergam

Dentro do Docker:

- a aplicação usa `http://localstack:4566`

Fora do Docker, executando localmente na máquina:

- a aplicação deve usar `http://localhost:4566`

Esse ponto é essencial para evitar erro de conexão.

---

## Dockerfile

O `Dockerfile` prepara um ambiente Python com Java para execução do PySpark.

Elementos principais:

- imagem base Python 3.10;
- instalação de Java 17;
- instalação das dependências Python;
- cópia do código-fonte e testes;
- definição de `PYTHONPATH=/app/src`.

No ambiente local, o Java acompanha a versão do PySpark instalada via `requirements.txt`.
No ambiente AWS Glue, o runtime é fornecido pela própria AWS.

---

## Execução Local: Formas Suportadas

### Modo 1: tudo em Docker

Executa LocalStack, bootstrap e aplicação em containers.

Subida:

```bash
docker compose up -d --build
```

Executar o job:

```bash
docker compose run --rm app
```

Esse modo é útil para validar rapidamente o fluxo completo.

### Modo 2: LocalStack em Docker e aplicação rodando local

Esse é o modo mais indicado para desenvolvimento diário e debug em IDE.

Fluxo:

- sobe apenas os serviços AWS simulados;
- executa o Python localmente;
- permite breakpoint, inspeção de variáveis e debug natural no PyCharm.

Subida apenas do LocalStack:

```bash
docker compose up -d localstack
```

Depois disso, o bootstrap pode ser executado localmente:

```bash
python -m jobs.localstack_bootstrap
```

E então o job:

```bash
python -m jobs.tailor_proposal_job
```

---

## Passo a Passo para Rodar Localmente Fora do Docker

### 1. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Definir `PYTHONPATH`

Linux/macOS:

```bash
export PYTHONPATH=src
```

### 3. Subir apenas o LocalStack

```bash
docker compose up -d localstack
```

### 4. Configurar variáveis de ambiente

Exemplo:

```bash
export JOB_NAME=tailor-proposal-local
export AWS_REGION=sa-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

export DYNAMODB_TABLE=tb_gm3_tailor_proposal
export DYNAMODB_GSI_NAME=gsi_startAt
export DYNAMODB_PARTITION_KEY_NAME=staticPartitionKey
export DYNAMODB_PARTITION_KEY_VALUE=TAILOR
export DYNAMODB_SORT_KEY_NAME=startAt
export DATABASE_NAME_WRITE=db_corp_canaisnaoassistidod_canaldigitalcorretora_sor_01
export TABLE_NAME_WRITE=tb_gm3_tailor_proposal
export EXECUTION_PARAMETER=/local/tailor/glue-execution-date

export AWS_ENDPOINT_URL=http://localhost:4566
export MESH_WRITE_MODE=local
export MESH_OUTPUT_LOCATION=$(pwd)/data/mesh/tb_gm3_tailor_proposal
export ENABLE_INCREMENTAL=false
export INCREMENTAL_COMPARISON_MODE=gt_plus_1_day
```

### 5. Inicializar recursos locais

```bash
python -m jobs.localstack_bootstrap
```

### 6. Executar o job

```bash
python -m jobs.tailor_proposal_job
```

---

## Sugestão de Arquivo `.env.local`

Para evitar exportar variáveis manualmente toda vez, recomenda-se criar um arquivo local, por exemplo `.env.local`, não versionado.

Exemplo:

```env
JOB_NAME=tailor-proposal-local
AWS_REGION=sa-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

DYNAMODB_TABLE=tb_gm3_tailor_proposal
DYNAMODB_GSI_NAME=gsi_startAt
DYNAMODB_PARTITION_KEY_NAME=staticPartitionKey
DYNAMODB_PARTITION_KEY_VALUE=TAILOR
DYNAMODB_SORT_KEY_NAME=startAt
DATABASE_NAME_WRITE=db_corp_canaisnaoassistidod_canaldigitalcorretora_sor_01
TABLE_NAME_WRITE=tb_gm3_tailor_proposal
EXECUTION_PARAMETER=/local/tailor/glue-execution-date

AWS_ENDPOINT_URL=http://localhost:4566
MESH_WRITE_MODE=local
MESH_OUTPUT_LOCATION=/caminho/absoluto/para/o/projeto/data/mesh/tb_gm3_tailor_proposal
ENABLE_INCREMENTAL=false
INCREMENTAL_COMPARISON_MODE=gt_plus_1_day
```

Carregamento:

```bash
set -a
source .env.local
set +a
```

---

## Passo a Passo para Debug no PyCharm

### Objetivo

Permitir que a aplicação rode localmente, mas consumindo DynamoDB e SSM do LocalStack.

### 1. Abrir o projeto

Abrir a raiz do projeto no PyCharm.

### 2. Configurar o interpretador

Selecionar o interpretador do ambiente virtual `.venv`.

### 3. Criar configuração de execução

Criar uma configuração do tipo Python com:

- módulo: `jobs.tailor_proposal_job`
- working directory: raiz do projeto
- environment variables: mesmas variáveis descritas acima

Se o PyCharm pedir script em vez de módulo, também é possível executar apontando para:

- `src/jobs/tailor_proposal_job.py`

Mas o formato por módulo costuma funcionar melhor quando `PYTHONPATH=src` está configurado.

### 4. Definir `PYTHONPATH`

Garantir que o `src` esteja no path:

- via variável `PYTHONPATH=src`;
- ou marcando `src` como source root no PyCharm.

### 5. Subir o LocalStack

Antes do debug:

```bash
docker compose up -d localstack
```

### 6. Rodar o bootstrap

Uma vez por ambiente local inicial:

```bash
python -m jobs.localstack_bootstrap
```

### 7. Colocar breakpoints

Pontos comuns para debug:

- `src/jobs/job_runner.py`
- `src/readers/dynamodb_reader.py`
- `src/services/parameter_store_service.py`
- `src/services/dataframe_service.py`

### 8. Iniciar o debug

Executar a configuração no modo `Debug`.

---

## Estado Atual do Ambiente Local

Quando o bootstrap é executado, o ambiente fica assim:

### DynamoDB

- tabela: `tb_gm3_tailor_proposal`
- chave primária:
  - `staticPartitionKey` como HASH
  - `proposalID` como RANGE
- GSI:
  - `gsi_startAt`
  - HASH: `staticPartitionKey`
  - RANGE: `startAt`

### SSM Parameter Store

- parâmetro: `/local/tailor/glue-execution-date`
- valor inicial: `" "` (espaço em branco)

### Registros de exemplo

Dois itens são criados para testes:

- `p-001` com `startAt=20260615`
- `p-002` com `startAt=20260618`

---

## Como Evoluir para Outras Tabelas

Para reaproveitar essa arquitetura em outras tabelas, o caminho recomendado é:

### 1. Definir constantes do novo domínio

Criar ou ajustar:

- nome da tabela DynamoDB;
- colunas esperadas;
- mapeamento de rename;
- configuração do destino.

### 2. Ajustar o bootstrap local

Se a nova tabela tiver estrutura diferente:

- ajustar criação de tabela;
- ajustar seed de dados;
- ajustar índice secundário, se necessário.

### 3. Avaliar se o `DynamoDBReader` continua genérico o suficiente

Hoje ele atende bem ao caso atual. Se surgirem diferenças fortes entre tabelas, pode ser melhor:

- manter um reader base;
- criar readers específicos por tabela/domínio.

### 4. Criar novo entrypoint em `jobs/`

Exemplo:

- `src/jobs/minha_nova_tabela_job.py`

Assim cada tabela tem seu ponto de entrada próprio, sem misturar regras de negócio.

### 5. Criar testes específicos

Adicionar:

- testes unitários das regras novas;
- testes de integração para o fluxo local.

---

## Melhorias Recomendadas para Próximas Fases

### Curto prazo

- fortalecer validação de schema de entrada e saída;
- separar melhor configuração local e AWS real.

### Médio prazo

- adicionar validação explícita do formato `YYYYMMDD`;
- enriquecer logs com contagem de registros gravados;
- criar uma camada de schema esperado para cada domínio.

### Produção

- habilitar incremental por configuração no ambiente produtivo quando a estratégia estiver homologada;
- provisionar índice via infraestrutura, não no job;
- adicionar observabilidade, métricas e alarmes.

---

## Decisões Arquiteturais Importantes

### 1. Execução local sem Glue real

O projeto foi desenhado para funcionar sem a library `awsglue`, usando:

- Spark local;
- `LocalJob`;
- resolução de parâmetros via variáveis de ambiente.

### 2. LocalStack como simulador AWS

Permite reproduzir localmente DynamoDB e SSM com baixo custo e rápida inicialização.

### 3. Escrita local em Parquet

A escrita local foi simplificada para filesystem, o que reduz dependências e facilita o debug.

### 4. Bootstrap separado da aplicação

A preparação do ambiente foi isolada para:

- evitar lógica de criação de infraestrutura dentro do job principal;
- permitir repetição controlada do processo;
- suportar execução local fora do container.

---

## Riscos e Cuidados

### `Scan` em produção

O incremental atual ainda usa `scan`, o que não é o ideal para grandes volumes.

### Dependência do formato de data

O campo `startAt` precisa continuar no formato `YYYYMMDD`.

### Diferença entre endpoint local e container

Nunca confundir:

- `http://localstack:4566` dentro do Docker;
- `http://localhost:4566` fora do Docker.

### Parameter Store e string vazia

O SSM não aceita `""` como valor. Por isso o valor inicial é `" "` e o código trata isso como vazio lógico.

---

## Resumo Final

Este projeto foi estruturado para permitir:

- execução local com baixo atrito;
- depuração simples em IDE;
- separação clara entre orquestração, leitura, transformação e escrita;
- evolução futura para Glue real e leitura incremental mais eficiente.

O padrão atual já é suficiente para servir como base de novos jobs, desde que a evolução preserve:

- responsabilidades bem separadas;
- configuração fora do código;
- infraestrutura local reproduzível;
- readers e writers desacoplados da orquestração.
