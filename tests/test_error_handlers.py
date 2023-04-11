from unittest.mock import sentinel

import pytest

from rest_api_client_toolkit.error_handlers import BaseErrorHandler
from rest_api_client_toolkit.response import RequestsResponse


class TestBaseExceptionHandler:
    handler = BaseErrorHandler

    def test_get_exception_needs_implementation(self):
        with pytest.raises(NotImplementedError):
            self.handler.get_exception(RequestsResponse(sentinel.response))
