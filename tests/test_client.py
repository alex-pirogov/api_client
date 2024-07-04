from typing import Any

import pytest
from pydantic_core import Url

from api_client.client import ApiClient
from api_client.request_config import HttpMethod, RequestConfig


@pytest.fixture
def api_client():
    return ApiClient(Url('https://petstore.swagger.io'))


class TestApiClient:
    @pytest.mark.parametrize(
        'config, url',
        (
            (
                RequestConfig(
                    method=HttpMethod.GET,
                ),
                'https://petstore.swagger.io',
            ),
            (
                RequestConfig(
                    method=HttpMethod.GET,
                    url='/v2/pet/findByStatus',
                ),
                'https://petstore.swagger.io/v2/pet/findByStatus',
            ),
            (
                RequestConfig(
                    method=HttpMethod.GET,
                    url='/v2/pet/findByStatus',
                    query_params={'status': 'available', '0hello': 'world', '.asd': '3'},
                ),
                (
                    'https://petstore.swagger.io/v2/pet/findByStatus'
                    '?status=available&0hello=world&.asd=3'
                ),
            ),
            (
                RequestConfig(
                    method=HttpMethod.GET,
                    query_params={'status': 'available', '0hello': 'world', '.asd': '3'},
                ),
                'https://petstore.swagger.io?status=available&0hello=world&.asd=3',
            ),
        ),
    )
    def test_get_url(self, api_client: ApiClient, config: RequestConfig[Any], url: str):
        assert api_client.get_url(config) == url
