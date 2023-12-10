import json
from logging import getLogger, config as loggingConfig
from requests.exceptions import ConnectionError
from typing import Any
from aiven.client.client import AivenClient, ResponseError


class MetadataParserClient(AivenClient):
    """MetadataParserClient is a wrapper for aiven-client."""

    def __init__(
        self, base_url: str, show_http: bool = False, request_timeout: int | None = None
    ) -> None:
        super(MetadataParserClient, self).__init__(
            base_url=base_url, show_http=show_http, request_timeout=request_timeout
        )
        self.log = getLogger("MetadataParserClient")
        with open("logging.json") as json_file:
            logConfigDict = json.load(json_file)
        loggingConfig.dictConfig(logConfigDict)

    def get_service(self, project: str, service: str) -> dict[str, Any]:
        """
        override get_service from AivenClient
        handles raised exceptions from get_service and continues excecution
        unexpected exceptions are left unhandled
        """

        try:
            return super().get_service(project=project, service=service)
        except (ConnectionError, ResponseError) as ex:
            self.log.warning(
                "Error while getting service: %s in project: %s", service, project
            )
            self.log.debug("Inner Exception: %s", ex)

        return {}
