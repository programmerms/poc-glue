# 05-POC-LOCAL.md

# Contexto Atualizado (POC Local)

Este documento consolida o contexto operacional e técnico para a POC local do Job que extrai dados do DynamoDB e publica no Data Mesh.

O objetivo é permitir que outros times (ou outras IAs) entendam rapidamente:

- o que o Job faz;
- como a data de corte funciona (full vs incremental);
- como executar e validar localmente usando Docker + LocalStack.

---

# Visão Geral do Fluxo

```
DynamoDB (origem)
   |
   | 1) Leitura (FULL ou INCREMENTAL)
   v
Glue Job (PySpark)
   |
   | 2) Padronização + particionamento (ano_mes_dia)
   v
Data Mesh (Parquet particionado)
   |
   | 3) Atualiza data de corte (SSM Parameter Store) somente em sucesso
   v
SSM Parameter Store
```

---

# Regras de Execução (Data de Corte)

- O parâmetro do SSM armazena a última data de execução no formato `YYYYMMDD` (ex: `20260618`).
- Regra:
  - se o parâmetro estiver ausente, vazio, nulo ou não for possível ler: executar **FULL** (Scan completo);
  - caso contrário: executar **INCREMENTAL**, usando a data do parâmetro como corte.

Na POC, o incremental é implementado como **Scan + FilterExpression** em `startAt >= YYYYMMDD`.

---

# Dados

## DynamoDB

- Tabela: `tb_gm3_tailor_proposal`
- Campo de corte: `startAt` (string `YYYYMMDD`)
- Colunas esperadas:
  - `proposalID`
  - `clientdID`
  - `clientType`
  - `deleted`
  - `functional`
  - `productDescription`
  - `productId`
  - `proposalSequence`
  - `startAt`
  - `staticPartitionKey`
  - `#st` (renomeada para `st` no DataFrame por compatibilidade)
  - `statusHubin`
  - `enviado`

## Data Mesh

- Database: `db_corp_canaisnaoassistidod_canaldigitalcorretora_sor_01`
- Tabela: `tb_gm3_tailor_proposal`
- Partição: `ano_mes_dia`
- Formato: Parquet
- Location (AWS): `s3://itau-corp-sor-sa-east-1-<conta-ambiente>/tb_gm3_tailor_proposal`

Na POC local, a escrita é realizada em filesystem como dataset Parquet particionado (configurável via `MESH_OUTPUT_LOCATION`).

---

# Configuração (POC Local)

Variáveis usadas na execução local:

- `AWS_REGION`
- `AWS_ENDPOINT_URL` (LocalStack)
- `DYNAMODB_TABLE`
- `EXECUTION_PARAMETER`
- `MESH_OUTPUT_LOCATION`
- `DATABASE_NAME_WRITE`
- `TABLE_NAME_WRITE`

O repositório disponibiliza um `.env.example` com todas as chaves necessárias.

---

# Execução Local

1. Subir containers:

```
docker compose up -d --build
```

2. Rodar o Job:

```
docker compose run --rm app
```

3. Rodar testes:

```
docker compose run --rm app pytest -q
docker compose run --rm app pytest -q -m integration
```

---

# Fases de Implementação (Roadmap)

## Fase 1 (POC local / FULL)

- Leitura: DynamoDB Scan
- Transformação: renomear `#st` → `st`, selecionar colunas e adicionar `ano_mes_dia`
- Escrita: Parquet particionado (local)
- Controle: atualizar data no SSM apenas em sucesso

## Fase 2 (INCREMENTAL simples)

- Leitura incremental: Scan + FilterExpression em `startAt >= data_corte`
- Mantém o restante do fluxo idêntico

## Fase 3 (INCREMENTAL eficiente)

- Evoluir para `Query` utilizando índice no DynamoDB (GSI) compatível com o corte por `startAt`
- Ajustar validações e observabilidade (métricas e contagens)

