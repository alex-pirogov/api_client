import json
import logging
from abc import ABC
from contextlib import asynccontextmanager
from logging import Logger
from typing import Any, Callable, Dict, Optional, Type
from urllib.parse import urlencode

from aiohttp import BasicAuth, ClientResponse, ClientSession
from pydantic import AnyHttpUrl, TypeAdapter

from .request_config import RequestConfig

ResponsePreprocessor = Callable[[dict[str, Any]], dict[str, Any]]


class ApiClientError(Exception):
    def __init__(self, config: RequestConfig[Any], status: int, text: str) -> None:
        self.request = config
        self.status = status
        self.text = text
        super().__init__()

    def __str__(self) -> str:
        return f"[{self.status}] {self.text if self.text else '*no content*'}"


class ApiClient(ABC):
    api_client_error_class: Type[ApiClientError] = ApiClientError
    response_preprocessors: list[ResponsePreprocessor] = []

    def __init__(
        self,
        base_url: AnyHttpUrl,
        logger: Logger | None = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[BasicAuth] = None,
    ) -> None:
        self.base_url = base_url
        self.logger = logger
        self.headers = headers or {}
        self.auth = auth

    def get_url[ReturnType](self, config: RequestConfig[ReturnType]) -> str:
        url = str(self.base_url).removesuffix('/') + config.url

        if config.query_params:
            url += '?' + urlencode(config.query_params, doseq=config.self_query_params_doseq)

        return url

    async def check_response(self, response: ClientResponse, config: RequestConfig[Any]) -> None:
        if response.status < 400:
            return

        if response.status not in config.allowed_error_codes:
            await self.log_request(response, config, logging.ERROR)
            raise self.api_client_error_class(config, response.status, await response.text())

    async def parse_response[
        ReturnType
    ](self, response: ClientResponse, config: RequestConfig[ReturnType]) -> ReturnType:
        if config.return_type is type(None):
            return config.return_type()

        response_json = await response.json()

        for preprocessor in self.response_preprocessors:
            response_json = preprocessor(response_json)

        return TypeAdapter(config.return_type).validate_python(response_json)

    async def log_request(
        self, response: ClientResponse, config: RequestConfig[Any], level: int = logging.DEBUG
    ) -> None:
        if not self.logger:
            return

        status, content = response.status, await response.text()

        text = f"[{config.method}] -> {status}\nURL: {config.url}\n"
        if config.payload:
            text += f"PAYLOAD:\n{json.dumps(config.payload, ensure_ascii=False, indent=2)}\n"

        text += f"RESP:\n{content if content else '*no content*'}"
        self.logger.log(level, text)

    @asynccontextmanager
    async def get_session[ReturnType](self, config: RequestConfig[ReturnType]):
        async with ClientSession(
            headers={**self.headers, **config.headers}, auth=self.auth
        ) as session:
            yield session

    @asynccontextmanager
    async def session_request[
        ReturnType
    ](self, session: ClientSession, config: RequestConfig[ReturnType]):
        async with session.request(
            method=config.method,
            url=self.get_url(config),
            json=config.payload,
        ) as response:
            yield response

    async def make_request[ReturnType](self, config: RequestConfig[ReturnType]) -> ReturnType:
        async with self.get_session(config) as session:
            async with self.session_request(session, config) as response:
                await response.read()
                await self.check_response(response, config)
                await self.log_request(response, config)
                return await self.parse_response(response, config)
