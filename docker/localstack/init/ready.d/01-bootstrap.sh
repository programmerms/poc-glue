#!/usr/bin/env bash
set -euo pipefail

TABLE_NAME="${DYNAMODB_TABLE_NAME:-tb_gm3_tailor_proposal}"
PARAM_NAME="${EXECUTION_PARAMETER_NAME:-/local/tailor/glue-execution-date}"

awslocal dynamodb create-table \
  --table-name "${TABLE_NAME}" \
  --attribute-definitions \
    AttributeName=staticPartitionKey,AttributeType=S \
    AttributeName=proposalID,AttributeType=S \
    AttributeName=startAt,AttributeType=S \
  --key-schema \
    AttributeName=staticPartitionKey,KeyType=HASH \
    AttributeName=proposalID,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes '[
    {
      "IndexName":"gsi_startAt",
      "KeySchema":[
        {"AttributeName":"staticPartitionKey","KeyType":"HASH"},
        {"AttributeName":"startAt","KeyType":"RANGE"}
      ],
      "Projection":{"ProjectionType":"ALL"}
    }
  ]' \
  >/dev/null 2>&1 || true

awslocal ssm put-parameter \
  --name "${PARAM_NAME}" \
  --type String \
  --value " " \
  --overwrite \
  >/dev/null

awslocal s3 mb s3://local-mesh >/dev/null 2>&1 || true

awslocal dynamodb put-item \
  --table-name "${TABLE_NAME}" \
  --item '{
    "staticPartitionKey": {"S": "TAILOR"},
    "proposalID": {"S": "p-001"},
    "clientdID": {"S": "c-001"},
    "clientType": {"S": "PF"},
    "deleted": {"BOOL": false},
    "functional": {"BOOL": true},
    "productDescription": {"S": "Produto A"},
    "productId": {"S": "prod-001"},
    "proposalSequence": {"N": "1"},
    "startAt": {"S": "20260615"},
    "#st": {"S": "CREATED"},
    "statusHubin": {"S": "OK"},
    "enviado": {"BOOL": true}
  }' \
  >/dev/null 2>&1 || true

awslocal dynamodb put-item \
  --table-name "${TABLE_NAME}" \
  --item '{
    "staticPartitionKey": {"S": "TAILOR"},
    "proposalID": {"S": "p-002"},
    "clientdID": {"S": "c-002"},
    "clientType": {"S": "PJ"},
    "deleted": {"BOOL": false},
    "functional": {"BOOL": true},
    "productDescription": {"S": "Produto B"},
    "productId": {"S": "prod-002"},
    "proposalSequence": {"N": "2"},
    "startAt": {"S": "20260618"},
    "#st": {"S": "APPROVED"},
    "statusHubin": {"S": "OK"},
    "enviado": {"BOOL": false}
  }' \
  >/dev/null 2>&1 || true
