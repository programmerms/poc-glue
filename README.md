# Glue Job DynamoDB -> Data Mesh

Projeto Glue Job para o fluxo **DynamoDB -> SSM Parameter Store -> Glue Job (PySpark) -> Data Mesh**.

A escrita oficial de produção é via `saveAsTable()` no Glue Catalog.
Para debug e testes locais, o projeto mantém um modo local com escrita em Parquet.

## Pré-requisitos

- Docker + Docker Compose

## Configuração

- Copie o arquivo `.env.example` para `.env` e ajuste se necessário.
- Para debug local fora do Docker, copie `.env.local.example` para `.env.local`.
- A saída Parquet local é gravada em `./data/mesh/` no modo `MESH_WRITE_MODE=local`.

## Subir o ambiente local

```bash
docker compose up -d --build
```

O LocalStack inicializa automaticamente:

- tabela DynamoDB `tb_gm3_tailor_proposal` (PK=staticPartitionKey, SK=proposalID)
- parâmetro SSM `/local/tailor/glue-execution-date` (valor em branco)
- GSI `gsi_startAt`
- 2 itens de exemplo no DynamoDB

## Executar o Job

Dentro do Docker:

```bash
docker compose run --rm app
```

## Executar Localmente

Subir apenas o LocalStack:

```bash
docker compose up -d localstack
```

Carregar configuração local:

```bash
set -a
source .env.local
set +a
export PYTHONPATH=src
```

Inicializar recursos locais:

```bash
python -m jobs.localstack_bootstrap
```

Executar o job localmente:

```bash
python -m jobs.tailor_proposal_job
```

## Rodar testes

Unitários:

```bash
docker compose run --rm app pytest -q
```

Integração com LocalStack:

```bash
docker compose run --rm app pytest -q -m integration
```
