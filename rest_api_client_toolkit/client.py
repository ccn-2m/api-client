import logging
from copy import copy
from typing import Any, Optional, Type

from rest_api_client_toolkit.authentication_methods import BaseAuthenticationMethod, NoAuthentication
from rest_api_client_toolkit.error_handlers import BaseErrorHandler, ErrorHandler
from rest_api_client_toolkit.request_formatters import BaseRequestFormatter, NoOpRequestFormatter
from rest_api_client_toolkit.request_strategies import BaseRequestStrategy, RequestStrategy
from rest_api_client_toolkit.response_handlers import BaseResponseHandler, RequestsResponseHandler
from rest_api_client_toolkit.utils.typing import OptionalDict

LOG = logging.getLogger(__name__)

# Timeout in seconds (float)
DEFAULT_TIMEOUT = 10.0


class APIClient:
    def __init__(
        self,
        authentication_method: Optional[BaseAuthenticationMethod] = None,
        response_handler: Type[BaseResponseHandler] = RequestsResponseHandler,
        request_formatter: Type[BaseRequestFormatter] = NoOpRequestFormatter,
        error_handler: Type[BaseErrorHandler] = ErrorHandler,
        request_strategy: Optional[BaseRequestStrategy] = None,
    ):
        # Set default values
        self._default_headers = {}
        self._default_query_params = {}
        self._default_username_password_authentication = None
        # A session needs to live at this client level so that all
        # request strategies have access to the same session.
        self._session = None

        # Set client strategies
        self.set_authentication_method(authentication_method or NoAuthentication())
        self.set_response_handler(response_handler)
        self.set_error_handler(error_handler)
        self.set_request_formatter(request_formatter)
        self.set_request_strategy(request_strategy or RequestStrategy())

        # Perform any one time authentication required by api
        self._authentication_method.perform_initial_auth(self)

    def get_session(self) -> Any:
        return self._session

    def set_session(self, session: Any):
        self._session = session

    def set_authentication_method(self, authentication_method: BaseAuthenticationMethod):
        if not isinstance(authentication_method, BaseAuthenticationMethod):
            raise RuntimeError(
                "provided authentication_method must be an instance of BaseAuthenticationMethod."
            )
        self._authentication_method = authentication_method

    def get_authentication_method(self) -> BaseAuthenticationMethod:
        return self._authentication_method

    def get_response_handler(self) -> Type[BaseResponseHandler]:
        return self._response_handler

    def set_response_handler(self, response_handler: Type[BaseResponseHandler]):
        if not (response_handler and issubclass(response_handler, BaseResponseHandler)):
            raise RuntimeError("provided response_handler must be a subclass of BaseResponseHandler.")
        self._response_handler = response_handler

    def get_error_handler(self) -> Type[BaseErrorHandler]:
        return self._error_handler

    def set_error_handler(self, error_handler: Type[BaseErrorHandler]):
        if not (error_handler and issubclass(error_handler, BaseErrorHandler)):
            raise RuntimeError("provided error_handler must be a subclass of BaseErrorHandler.")
        self._error_handler = error_handler

    def get_request_formatter(self) -> Type[BaseRequestFormatter]:
        return self._request_formatter

    def set_request_formatter(self, request_formatter: Type[BaseRequestFormatter]):
        if not (request_formatter and issubclass(request_formatter, BaseRequestFormatter)):
            raise RuntimeError("provided request_formatter must be a subclass of BaseRequestFormatter.")
        self._request_formatter = request_formatter

    def get_request_strategy(self) -> BaseRequestStrategy:
        return self._request_strategy

    def set_request_strategy(self, request_strategy: BaseRequestStrategy):
        if not isinstance(request_strategy, BaseRequestStrategy):
            raise RuntimeError("provided request_strategy must be an instance of BaseRequestStrategy.")
        self._request_strategy = request_strategy
        self._request_strategy.set_client(self)

    def get_default_headers(self) -> dict:
        headers = {}
        for strategy in (self._authentication_method, self._request_formatter):
            headers.update(strategy.get_headers())
        return headers

    def get_default_query_params(self) -> dict:
        return self._authentication_method.get_query_params()

    def get_default_username_password_authentication(self) -> Optional[tuple]:
        return self._authentication_method.get_username_password_authentication()

    def get_request_timeout(self) -> float:
        """Return the number of seconds before the request times out."""
        return DEFAULT_TIMEOUT

    def clone(self):
        """Enable Prototype pattern on client."""
        return copy(self)

    def post(self, endpoint: str, data: dict, params: OptionalDict = None, **kwargs):
        """Send data and return response data from POST endpoint."""
        LOG.debug("POST %s with %s", endpoint, data)
        return self.get_request_strategy().post(endpoint, data=data, params=params, **kwargs)

    def get(self, endpoint: str, params: OptionalDict = None, **kwargs):
        """Return response data from GET endpoint."""
        LOG.debug("GET %s", endpoint)
        return self.get_request_strategy().get(endpoint, params=params, **kwargs)

    def put(self, endpoint: str, data: dict, params: OptionalDict = None, **kwargs):
        """Send data to overwrite resource and return response data from PUT endpoint."""
        LOG.debug("PUT %s with %s", endpoint, data)
        return self.get_request_strategy().put(endpoint, data=data, params=params, **kwargs)

    def patch(self, endpoint: str, data: dict, params: OptionalDict = None, **kwargs):
        """Send data to update resource and return response data from PATCH endpoint."""
        LOG.debug("PATCH %s with %s", endpoint, data)
        return self.get_request_strategy().patch(endpoint, data=data, params=params, **kwargs)

    def delete(self, endpoint: str, params: OptionalDict = None, **kwargs):
        """Remove resource with DELETE endpoint."""
        LOG.debug("DELETE %s", endpoint)
        return self.get_request_strategy().delete(endpoint, params=params, **kwargs)
