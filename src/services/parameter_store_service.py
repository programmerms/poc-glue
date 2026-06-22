"""
Serviço responsável por realizar operações no AWS Systems Manager Parameter Store.
"""

from typing import Optional

import boto3
from botocore.exceptions import ClientError


class ParameterStoreService:
    """
    Serviço responsável pela leitura e atualização de parâmetros
    no AWS Systems Manager Parameter Store.
    """

    def __init__(
        self,
        region_name: str,
        endpoint_url: Optional[str] = None,
    ):
        self._client = boto3.client(
            "ssm",
            region_name=region_name,
            endpoint_url=endpoint_url,
        )

    def get_parameter(self, parameter_name: str) -> Optional[str]:
        """
        Recupera o valor de um parâmetro.

        Args:
            parameter_name: Nome do parâmetro.

        Returns:
            Valor armazenado ou None caso não exista.
        """

        try:

            response = self._client.get_parameter(
                Name=parameter_name
            )

            return response["Parameter"]["Value"]

        except self._client.exceptions.ParameterNotFound:
            return None

        except ClientError:
            raise

    def update_parameter(
        self,
        parameter_name: str,
        value: str
    ) -> None:
        """
        Atualiza o valor de um parâmetro.

        Args:
            parameter_name: Nome do parâmetro.
            value: Novo valor.
        """

        self._client.put_parameter(
            Name=parameter_name,
            Value=value,
            Type="String",
            Overwrite=True
        )
