# 01-PROJETO.md

# Projeto

## Nome

AWS Glue Job - DynamoDB → Data Mesh

---

# Objetivo

Este projeto tem como objetivo extrair informações de uma tabela do Amazon DynamoDB utilizando AWS Glue e disponibilizar os dados no Data Mesh corporativo através de tabelas Hive armazenadas em formato Parquet.

A solução foi projetada para suportar dois modos de execução:

* Extração Full
* Extração Incremental

Inicialmente será implementada apenas a extração Full para validação do fluxo completo. Após a estabilização da solução, será adicionada a extração Incremental utilizando a data da última execução armazenada no AWS Systems Manager Parameter Store.

---

# Fluxo da Solução

```text
Scheduler
    │
    ▼
Glue Job
    │
    ▼
JobRunner.execute()
    │
    ├──────────────► ParameterStoreService
    │                     │
    │                     ▼
    │             Obtém última execução
    │
    ├──────────────► ExecutionDateService
    │                     │
    │                     ▼
    │        Define FULL ou INCREMENTAL
    │
    ├──────────────► DynamoDBReader
    │                     │
    │                     ▼
    │           Spark DataFrame
    │
    ├──────────────► DataFrameService
    │                     │
    │                     ▼
    │   Rename + Cast + Coluna ano_mes_dia
    │
    ├──────────────► MeshWriter
    │                     │
    │                     ▼
    │      Hive saveAsTable()
    │
    ├──────────────► ParameterStoreService
    │                     │
    │                     ▼
    │      Atualiza última execução
    │
    ▼
Job.commit()
```

---

# Escopo

O projeto será responsável por:

* Ler dados do Amazon DynamoDB.
* Converter os dados para Spark DataFrame.
* Padronizar o DataFrame.
* Escrever os dados no Data Mesh.
* Controlar a data da última execução através do Parameter Store.
* Permitir futura evolução para carga incremental.

Não faz parte do escopo:

* APIs.
* Lambda.
* Step Functions.
* Streaming.
* CDC.
* Iceberg.
* Processamentos distribuídos adicionais além do Spark do Glue.

---

# Tecnologias

* AWS Glue 4.0
* Python 3.10
* Apache Spark
* Spark SQL
* AWS Glue Catalog
* Amazon DynamoDB
* AWS Systems Manager Parameter Store
* Hive
* Parquet
* Amazon S3
* boto3

---

# Ambientes

A solução deverá funcionar nos ambientes:

* DEV
* HOMOLOG
* PRD

Todos os parâmetros sensíveis deverão ser definidos por configuração, permitindo reutilização do mesmo código entre ambientes.

---

# Estratégia de Extração

## Fase 1

Será executado um Full Scan da tabela do DynamoDB para validar toda a esteira de processamento.

Fluxo:

DynamoDB

↓

Scan()

↓

Spark DataFrame

↓

Data Mesh

---

## Fase 2

Após validação da carga Full será implementada a carga Incremental.

A leitura utilizará a data da última execução armazenada no Parameter Store para consultar apenas os registros alterados.

Inicialmente está prevista a utilização de índices do DynamoDB (Query), substituindo o Scan completo.

---

# Estratégia de Escrita

A escrita será realizada diretamente na tabela Hive existente utilizando:

* saveAsTable()
* formato Hive
* arquivos Parquet
* modo Append

Antes da gravação, o DataFrame deverá possuir exatamente a mesma ordem de colunas da tabela existente no Glue Catalog.

---

# Controle de Execução

A data da última execução será armazenada no AWS Systems Manager Parameter Store.

Formato:

YYYYMMDD

Exemplo:

20260616

Ao término de uma execução com sucesso:

* atualizar o Parameter Store;
* executar Job.commit().

Caso ocorra qualquer erro durante o processamento, a data não deverá ser atualizada.

---

# Estrutura do Projeto

```text
src/
│
├── config/
│   ├── glue_context_factory.py
│   ├── spark_config.py
│   └── settings.py
│
├── readers/
│   └── dynamodb_reader.py
│
├── writers/
│   └── mesh_writer.py
│
├── services/
│   ├── parameter_store_service.py
│   ├── execution_date_service.py
│   └── dataframe_service.py
│
├── utils/
│   ├── logger.py
│   ├── dates.py
│   └── validations.py
│
├── constants/
│   ├── parameters.py
│   └── tables.py
│
└── job.py
```

---

# Princípios do Projeto

O projeto deverá seguir os seguintes princípios durante todo o desenvolvimento:

* Código simples e de fácil manutenção.
* Arquitetura estável.
* Sem alterações estruturais sem necessidade.
* Sem criação de camadas desnecessárias.
* Classes com responsabilidade única.
* Código pronto para produção.
* Logging centralizado.
* Tipagem explícita.
* Docstrings em todas as classes públicas.
* Tratamento adequado de exceções.
* Configurações centralizadas.
* Reutilização de componentes.

---

# Objetivo Final

Ao término do projeto deverá existir um AWS Glue Job capaz de:

1. Ler dados do DynamoDB.
2. Transformar os dados utilizando Spark.
3. Escrever os dados no Data Mesh em formato Hive/Parquet.
4. Controlar automaticamente a última execução.
5. Evoluir facilmente de carga Full para Incremental sem alterações significativas na arquitetura.
