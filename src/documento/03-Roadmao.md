# 03-ROADMAP.md

# Roadmap Oficial de Implementação

**Versão:** 1.0

**Status:** Oficial

---

# Objetivo

Este documento define a sequência oficial de implementação do projeto.

Todo o desenvolvimento deverá seguir rigorosamente as entregas aqui descritas.

Nenhuma funcionalidade deverá ser implementada fora da ordem estabelecida, salvo decisão registrada em `04-DECISOES.md`.

---

# Estratégia de Desenvolvimento

O projeto será desenvolvido em pequenas entregas.

Cada entrega deverá atender aos seguintes critérios:

* Escopo bem definido
* Código funcional
* Código testável
* Código pronto para produção
* Sem dependências incompletas

Uma entrega somente será considerada concluída após validação completa.

---

# FASE 1 — Estrutura Base

## Entrega 1

### Configuração do Projeto

Objetivo:

Criar toda a estrutura inicial do projeto.

Itens:

* Estrutura de diretórios
* Ambiente Python
* Configuração do Glue
* Configuração do Spark
* Arquivos de configuração
* Organização inicial do projeto

Status:

⬜ Não iniciado

---

## Entrega 2

### Configuração Base

Objetivo:

Centralizar todas as configurações do projeto.

Itens:

* Configurações de ambiente
* Configurações do Spark
* Configurações do Glue
* Configurações do Data Catalog
* Configurações do S3

Status:

⬜ Não iniciado

---

## Entrega 3

### Constantes

Objetivo:

Centralizar todas as constantes do projeto.

Itens:

* Constantes de ambiente
* Constantes de tabelas
* Constantes de buckets
* Constantes de formatos
* Constantes de partições

Status:

⬜ Não iniciado

---

## Entrega 4

### Utilitários

Objetivo:

Criar funções reutilizáveis.

Itens:

* Manipulação de datas
* Conversões
* Funções auxiliares
* Helpers comuns

Status:

⬜ Não iniciado

---

# FASE 2 — Leitura dos Dados

## Entrega 5

### Readers

Objetivo:

Implementar a camada responsável pela leitura dos dados.

Itens:

* Reader Hive
* Reader S3
* Reader Data Catalog
* Leitura Full
* Leitura Incremental

Status:

⬜ Não iniciado

---

## Entrega 6

### Models

Objetivo:

Criar os modelos utilizados durante o processamento.

Itens:

* Objetos de domínio
* Estruturas auxiliares
* Tipagens compartilhadas

Status:

⬜ Não iniciado

---

# FASE 3 — Regras de Negócio

## Entrega 7

### Transformações

Objetivo:

Implementar todas as regras de transformação dos dados.

Itens:

* Limpeza
* Padronização
* Enriquecimento
* Conversões
* Regras de negócio

Status:

⬜ Não iniciado

---

## Entrega 8

### Services

Objetivo:

Orquestrar o fluxo de processamento.

Itens:

* Coordenação das leituras
* Execução das transformações
* Preparação para escrita

Status:

⬜ Não iniciado

---

# FASE 4 — Persistência

## Entrega 9

### Writers

Objetivo:

Implementar toda a escrita dos dados.

Itens:

* Escrita Hive
* Escrita Parquet
* Publicação no Catálogo
* Particionamento

Status:

⬜ Não iniciado

---

## Entrega 10

### Job Principal

Objetivo:

Criar o ponto de entrada oficial da aplicação.

Fluxo:

Leitura

↓

Transformação

↓

Validação

↓

Escrita

↓

Finalização

Status:

⬜ Não iniciado

---

# FASE 5 — Qualidade

## Entrega 11

### Logging

Objetivo:

Implementar o sistema de logs.

Itens:

* Início do Job
* Fim do Job
* Tempo de execução
* Quantidade de registros
* Tratamento de erros

Status:

⬜ Não iniciado

---

## Entrega 12

### Tratamento de Exceções

Objetivo:

Centralizar o tratamento de erros.

Itens:

* Exceções de leitura
* Exceções de transformação
* Exceções de escrita
* Logs de erro

Status:

⬜ Não iniciado

---

## Entrega 13

### Testes

Objetivo:

Garantir a qualidade do projeto.

Itens:

* Testes unitários
* Testes de integração
* Validação dos Jobs

Status:

⬜ Não iniciado

---

# FASE 6 — Finalização

## Entrega 14

### Documentação Técnica

Objetivo:

Atualizar toda a documentação do projeto.

Itens:

* README
* Exemplos de execução
* Fluxo do Job
* Diagramas
* Atualização da pasta docs/

Status:

⬜ Não iniciado

---

# Critérios para Conclusão

Uma entrega será considerada concluída somente quando:

* Todo o escopo estiver implementado.
* O código estiver revisado.
* Os testes estiverem aprovados.
* A documentação estiver atualizada.

---

# Regras do Desenvolvimento

Durante a implementação não será permitido:

* Alterar a arquitetura definida em `02-ARQUITETURA.md`.
* Criar funcionalidades fora da entrega atual.
* Adicionar dependências sem aprovação.
* Alterar a estrutura do projeto sem registro em `04-DECISOES.md`.
* Pular entregas.

---

# Controle de Evolução

Sempre que uma entrega for concluída:

* Atualizar este documento marcando a entrega como concluída.
* Registrar decisões relevantes em `04-DECISOES.md`.
* Prosseguir para a próxima entrega somente após validação.

---

# Documento Oficial

Este roadmap representa o planejamento oficial do projeto e deverá ser utilizado como referência durante todo o ciclo de desenvolvimento.
