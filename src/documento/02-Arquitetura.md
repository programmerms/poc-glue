# 02-ARQUITETURA.md

# Arquitetura Oficial do Projeto

**Versão:** 1.0

**Status:** Oficial

---

# Objetivo

Este documento define toda a arquitetura oficial do projeto.

As decisões aqui registradas são consideradas permanentes durante o desenvolvimento.

Nenhuma implementação poderá modificar esta arquitetura sem que uma nova decisão seja registrada previamente no documento `04-DECISOES.md`.

---

# Princípios Arquiteturais

O projeto foi concebido seguindo os seguintes princípios:

* Simplicidade
* Legibilidade
* Manutenibilidade
* Reutilização
* Escalabilidade
* Código pronto para produção
* Baixo acoplamento
* Alta coesão

Toda implementação deverá priorizar clareza ao invés de complexidade.

---

# Stack Tecnológica

## Linguagem

* Python 3.10

---

## Engine de Processamento

* AWS Glue 4.0

Baseado em:

* Apache Spark
* PySpark

---

## Catálogo de Dados

* AWS Glue Data Catalog

---

## Data Warehouse

* Apache Hive

Toda escrita deverá utilizar tabelas registradas no catálogo.

---

## Formato dos Dados

Formato oficial:

* Parquet

Não serão utilizados outros formatos, salvo decisão registrada oficialmente.

---

## Armazenamento

* Amazon S3

Organizado por ambientes.

Exemplo:

```
dev/

homolog/

prd/
```

---

# Arquitetura de Dados

O projeto seguirá o modelo **Data Mesh**.

Os domínios de dados serão independentes.

Cada domínio será responsável por:

* leitura
* transformação
* validação
* publicação

Não haverá dependência direta entre domínios.

---

# Fluxo Oficial

Todo Job seguirá exatamente o fluxo abaixo.

```
Leitura

↓

Validação

↓

Transformação

↓

Enriquecimento

↓

Padronização

↓

Escrita
```

Nenhuma etapa poderá ser ignorada.

---

# Estrutura do Projeto

A estrutura de diretórios será organizada da seguinte forma:

```
project/

docs/

config/

constants/

utils/

models/

services/

readers/

transformations/

writers/

jobs/

tests/
```

Cada diretório possui responsabilidade única.

---

# Organização das Camadas

## config

Responsável por:

* parâmetros
* ambientes
* configuração do Glue
* configuração Spark

---

## constants

Responsável apenas por constantes.

Não deverá conter lógica.

---

## utils

Funções utilitárias reutilizáveis.

Sem regra de negócio.

---

## models

Objetos utilizados durante o processamento.

---

## readers

Toda leitura de dados.

Exemplos:

* Hive
* S3
* Catálogo

Nenhuma transformação poderá ocorrer nesta camada.

---

## transformations

Toda regra de negócio.

Todas as transformações Spark deverão estar concentradas aqui.

---

## services

Coordenação das operações do projeto.

Sem acesso direto ao armazenamento.

---

## writers

Responsável exclusivamente pela persistência dos dados.

Toda escrita deverá ocorrer nesta camada.

---

## jobs

Ponto de entrada da aplicação.

Apenas orquestra o fluxo.

Não deverá conter regra de negócio.

---

## tests

Todos os testes automatizados.

---

# Estratégia de Leitura

Toda leitura deverá ocorrer através da camada Readers.

Tipos suportados:

* Full Load
* Incremental

A estratégia será definida conforme cada domínio.

---

# Estratégia de Escrita

Toda escrita deverá ocorrer através da camada Writers.

As tabelas deverão ser publicadas utilizando:

* saveAsTable()

Não será utilizada escrita direta em arquivos como estratégia principal.

---

# Organização do Spark

Será utilizada apenas uma SparkSession durante toda a execução do Job.

Não serão criadas múltiplas sessões.

---

# Logging

Todo logging será centralizado.

Os logs deverão informar:

* início do Job
* fim do Job
* tempo de execução
* quantidade de registros lidos
* quantidade de registros gravados
* erros

---

# Tratamento de Exceções

As exceções deverão ser tratadas de forma centralizada.

Não será permitido:

* capturar Exception sem tratamento
* ignorar erros silenciosamente

Todo erro deverá ser registrado em log.

---

# Configuração

Toda configuração deverá ser externa ao código.

Exemplos:

* ambiente
* banco
* catálogo
* bucket
* parâmetros

Não será permitido utilizar valores fixos ("hardcoded") para configurações de ambiente.

---

# Escalabilidade

A arquitetura deverá permitir:

* inclusão de novos domínios
* novos Jobs
* novos Readers
* novos Writers
* novas Transformações

Sem necessidade de alteração da estrutura existente.

---

# Restrições Arquiteturais

Durante o desenvolvimento NÃO será permitido:

* alterar a estrutura de pastas sem aprovação
* adicionar frameworks desnecessários
* criar abstrações sem necessidade
* duplicar lógica
* misturar leitura com transformação
* misturar transformação com escrita
* criar dependências circulares

---

# Alterações Futuras

Qualquer alteração arquitetural deverá seguir o fluxo:

1. Registrar a decisão em `04-DECISOES.md`
2. Atualizar este documento
3. Somente então implementar a alteração

Nenhuma exceção será permitida.

---

# Arquitetura Oficial

Este documento representa a arquitetura oficial do projeto.

Todo desenvolvimento deverá seguir rigorosamente as definições aqui estabelecidas.
