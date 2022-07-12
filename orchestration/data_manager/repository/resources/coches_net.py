import json
import logging
import time
import sys
from typing import Any, Dict, Optional, Iterator

import requests
from requests.exceptions import RequestException

from dagster import Failure, Field, get_dagster_logger, resource

API_BASE = "ms-mt--api-web.spain.advgo.net"

MAX_PAGE_SIZE = 100


class CochesNetResource:
    """
    This class exposes methods on top of the Motos/Coches.net API.
    """

    def __init__(
        self,
        target_market: str = "coches",
        request_max_retries: int = 3,
        request_retry_delay: float = 0.25,
        log: logging.Logger = get_dagster_logger(),
    ):
        self._request_max_retries = request_max_retries
        self._request_retry_delay = request_retry_delay
        assert target_market in {"coches", "motos"}
        self._target_market = target_market

        self._log = log

    @property
    def api_base_url(self) -> str:
        return f"https://{API_BASE}"

    @staticmethod
    def _construct_user_agent() -> str:
        """A helper method to construct a standard User-Agent string to be used in HTTP request
        headers.

        Returns:
            str: The constructed User-Agent value.
        """
        python_version = f"Python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        return python_version

    def _construct_headers(self, compressed=False) -> Dict[str, str]:
        """Constructs a standard set of headers for HTTP requests.

        Args:
            compressed (Optional[bool]): If the response should be sent compressed in gzip format

        Returns:
            Dict[str, str]: The HTTP request headers.
        """
        headers = requests.utils.default_headers()
        headers["User-Agent"] = self._construct_user_agent()
        headers["Content-Type"] = "application/json;charset=utf-8"
        headers["Accept"] = "application/json"
        headers["X-Schibsted-Tenant"] = self._target_market
        if compressed:
            headers["Accept-Encoding"] = "gzip, deflate, br"
        return headers

    def make_request(
        self, method: str, endpoint: str, data: str = None, compressed=False
    ) -> Dict[str, Any]:
        """
        Creates and sends a request to an endpoint.

        Args:
            method (str): The http method to use for this request (e.g. "POST", "GET", "PATCH").
            endpoint (str): The endpoint to send this request to.
            data (Optional[str]): JSON-formatted data string to be included in the request.
            compressed (Optional[bool]): If the response should be sent compressed in gzip format
        Returns:
            Dict[str, Any]: JSON data from the response to this request
        """
        headers = self._construct_headers(compressed)

        num_retries = 0
        while True:
            try:
                response = requests.request(
                    method=method,
                    url=f"{self.api_base_url}/{endpoint}",
                    headers=headers,
                    data=data,
                )
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                self._log.error("Request to Coches.Net API failed: %s", e)
                if num_retries == self._request_max_retries:
                    break
                num_retries += 1
                time.sleep(self._request_retry_delay)

        raise Failure("Exceeded max number of retries.")

    def search(self, limit: int = None) -> Iterator[Dict[str, Any]]:
        """
        Runs a paginated search in the API.

        Args:
            limit (Optional[int]): Limits the number of records that will be obtained from the API

        Returns:
            Iterator[Dict[str, Any]]: Generator with JSON data from all the paged responses to this request
        """
        num_page = 1
        num_records = 0
        total_pages = None
        finished = False
        self._log.info("Target market: %s", self._target_market)
        while not finished:
            data = {
                "pagination": {"page": num_page, "size": MAX_PAGE_SIZE},
                "sort": {"order": "desc", "term": "publishedDate"},
            }
            response = self.make_request(
                method="POST", endpoint="search", data=json.dumps(data)
            )
            if total_pages is None:
                total_pages = int(response["meta"]["totalPages"])
                self._log.info(
                    f"Estimated total records:  {total_pages*MAX_PAGE_SIZE} records"
                )
            if (num_page == total_pages) or (
                limit is not None and num_page * MAX_PAGE_SIZE >= limit
            ):
                finished = True
            num_page += 1
            num_records += len(response["items"])
            if num_records % 10000 == 0:
                self._log.info(f"Processed {num_records} records")
            yield from response["items"]


@resource(
    config_schema={
        "target_market": Field(
            str,
            default_value="coches",
            description="The market of vehicles that the API will target. `coches` will retrieve cars "
            "while `motos` will retrieve motorbikes.",
        ),
        "request_max_retries": Field(
            int,
            default_value=3,
            description="The maximum number of times requests to the API should be retried "
            "before failing.",
        ),
        "request_retry_delay": Field(
            float,
            default_value=0.25,
            description="Time (in seconds) to wait between each request retry.",
        ),
    },
    description="This resource helps manage connectors",
)
def coches_net_resource(context) -> CochesNetResource:
    """
    This resource allows users to programmatically interface with the Coches.net REST API to launch
    syncs and monitor their progress. This currently implements only a subset of the functionality
    exposed by the API.

    **Examples:**

    .. code-block:: python

        from dagster import job
        from orchestration.resources import coches_net_resource

        my_coches_resource = coches_net_resource.configured({})

        @job(resource_defs={"coches":my_coches_resource})
        def my_coches_job():
            ...

    """
    return CochesNetResource(
        target_market=context.resource_config["target_market"],
        request_max_retries=context.resource_config["request_max_retries"],
        request_retry_delay=context.resource_config["request_retry_delay"],
        log=context.log,
    )
