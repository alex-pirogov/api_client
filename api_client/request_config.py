import json
from abc import ABC
from enum import Enum
from typing import Any, TypeAlias

from pydantic import BaseModel

JSON: TypeAlias = dict[str, 'JSON'] | list['JSON'] | str | int | float | bool


class HttpMethod(str, Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    PATCH = 'patch'
    DELETE = 'delete'


def safe_dump(payload: BaseModel) -> JSON:
    return json.loads(payload.model_dump_json())


class GenericRequestConfig[ReturnType](ABC):
    def __init__(
        self,
        method: HttpMethod,
        url: str | None = None,
        query_params: dict[str, Any] | None = None,
        return_type: type[ReturnType] = type(None),
        payload: JSON | None = None,
        allowed_error_codes: list[int] | None = None,
        headers: dict[str, str] | None = None,
        self_query_params_doseq: bool = False,
    ) -> None:
        self.method = method
        self.url = url or ''
        self.query_params = query_params or {}
        self.payload = payload
        self.return_type = return_type
        self.allowed_error_codes = allowed_error_codes or []
        self.headers = headers or {}
        self.self_query_params_doseq = self_query_params_doseq


class RequestConfig[ReturnType](GenericRequestConfig[ReturnType]):
    pass
