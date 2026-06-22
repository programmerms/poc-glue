# 04-DECISOES.md

# Registro Oficial de Decisões

**Versão:** 1.0

**Status:** Oficial

---

# Objetivo

Este documento registra todas as decisões arquiteturais, técnicas e funcionais tomadas durante o desenvolvimento do projeto.

Seu principal objetivo é preservar o histórico das decisões, seus motivos e seus impactos, evitando que os mesmos assuntos sejam discutidos repetidamente.

Toda decisão registrada neste documento passa a fazer parte da arquitetura oficial do projeto.

---

# Regras de Utilização

Sempre que uma decisão alterar qualquer aspecto do projeto, deverá ser seguido o seguinte fluxo:

1. Registrar a decisão neste documento.
2. Atualizar a documentação afetada (`01`, `02`, `03`, `05` ou `06`).
3. Somente depois realizar a implementação.

Nenhuma alteração arquitetural deverá ser implementada sem o respectivo registro.

---

# Estrutura de Registro

Cada decisão deverá seguir obrigatoriamente o modelo abaixo.

```text
Data:

Categoria:

Título:

Contexto:

Decisão:

Motivação:

Impacto:

Documentos Atualizados:

Responsável:
```

---

# Categorias

As decisões deverão ser classificadas em uma das seguintes categorias:

* Arquitetura
* Infraestrutura
* Data Mesh
* Spark
* Glue
* Hive
* S3
* Modelagem
* Performance
* Segurança
* Logging
* Tratamento de Erros
* Convenções
* Organização do Projeto
* Testes
* Documentação
* Outros

---

# Registro das Decisões

## DEC-001

**Data**

AAAA-MM-DD

**Categoria**

Arquitetura

**Título**

Definição da arquitetura oficial do projeto.

**Contexto**

Início do desenvolvimento.

**Decisão**

Adotar uma arquitetura modular baseada em camadas bem definidas (`config`, `constants`, `utils`, `readers`, `transformations`, `services`, `writers` e `jobs`).

**Motivação**

Separar responsabilidades, facilitar manutenção e evolução.

**Impacto**

Toda implementação deverá respeitar essa estrutura.

**Documentos Atualizados**

* 02-ARQUITETURA.md

**Responsável**

Equipe do Projeto

---

## DEC-002

**Data**

AAAA-MM-DD

**Categoria**

Tecnologia

**Título**

Definição da stack tecnológica.

**Contexto**

Escolha das tecnologias base.

**Decisão**

Utilizar:

* Python 3.10
* AWS Glue 4.0
* Apache Spark
* PySpark
* Hive
* Parquet
* Amazon S3

**Motivação**

Padronização tecnológica e compatibilidade com o ambiente corporativo.

**Impacto**

Toda implementação deverá utilizar exclusivamente essa stack, salvo nova decisão registrada.

**Documentos Atualizados**

* 01-PROJETO.md
* 02-ARQUITETURA.md

---

## DEC-003

**Data**

AAAA-MM-DD

**Categoria**

Persistência

**Título**

Estratégia oficial de escrita.

**Contexto**

Definição da forma de publicação dos dados.

**Decisão**

A persistência oficial será realizada utilizando tabelas registradas no Glue Catalog, com escrita através de `saveAsTable()`.

**Motivação**

Padronização da publicação e integração com o Data Mesh.

**Impacto**

Não utilizar `save()` como estratégia principal de publicação.

**Documentos Atualizados**

* 02-ARQUITETURA.md
* 06-DATA_MESH.md

---

## DEC-004

**Data**

AAAA-MM-DD

**Categoria**

Arquitetura

**Título**

Separação de responsabilidades.

**Contexto**

Definição das responsabilidades de cada camada.

**Decisão**

Cada camada possuirá responsabilidade única:

* Readers → leitura
* Transformations → regras de negócio
* Services → orquestração
* Writers → persistência
* Jobs → inicialização e execução

**Motivação**

Evitar acoplamento e facilitar manutenção.

**Impacto**

Nenhuma camada poderá executar responsabilidades pertencentes a outra.

**Documentos Atualizados**

* 02-ARQUITETURA.md

---

## DEC-005

**Data**

AAAA-MM-DD

**Categoria**

Processamento

**Título**

Fluxo oficial do Job.

**Contexto**

Padronização da execução dos Jobs.

**Decisão**

Todo Job seguirá obrigatoriamente o fluxo:

```text
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

**Motivação**

Garantir uniformidade entre todos os pipelines.

**Impacto**

Todos os Jobs deverão seguir esse fluxo.

**Documentos Atualizados**

* 02-ARQUITETURA.md

---

# Decisões Pendentes

Esta seção será utilizada para registrar temas em análise que ainda não possuem definição oficial.

Modelo:

```text
Tema:

Descrição:

Alternativas:

Status:

Responsável:

Previsão de decisão:
```

---

# Histórico de Alterações

Sempre que uma decisão for alterada, manter o histórico.

Modelo:

```text
DEC-00X

Versão anterior:

Nova decisão:

Motivação da alteração:

Data:
```

O histórico nunca deverá ser removido.

---

# Boas Práticas

* Nunca excluir decisões antigas.
* Registrar o motivo de cada decisão.
* Atualizar os documentos afetados antes da implementação.
* Utilizar identificadores sequenciais (`DEC-001`, `DEC-002`, ...).
* Escrever decisões de forma objetiva e técnica.
* Manter rastreabilidade entre decisões, arquitetura e código.

---

# Documento Oficial

Este documento representa o histórico oficial das decisões do projeto.

Qualquer alteração arquitetural, tecnológica ou funcional deverá ser registrada aqui antes de ser implementada.
