from rest_api_client_toolkit.utils.typing import OptionalInt


class APIClientError(Exception):
    """General exception to denote that something went wrong when using the client.

    All other exceptions *must* inherit from this."""

    pass


class ResponseParseError(APIClientError):
    """Something went wrong when trying to parse the response."""

    pass


class APIRequestError(APIClientError):
    """Exception to denote that something went wrong when making the request."""

    message: str = ""
    status_code: OptionalInt = None
    info: str = ""

    def __init__(self, message: str = "", status_code: OptionalInt = None, info: str = ""):
        self.message = self.message or message
        self.status_code = self.status_code or status_code
        self.info = self.info or info

    def __str__(self):
        return self.message


class RedirectionError(APIRequestError):
    """A redirection status code (3xx) was returned as a final code when making the request.

    This means that no data can be returned to the client as we could not find the
    requested resource as it had moved.
    """

    pass


class ClientError(APIRequestError):
    """A client error status code (4xx) was returned as a final code when making the request.

    This is due primarily to user input by passing invalid data to the API
    """

    pass


class ServerError(APIRequestError):
    """A server error status code (5xx) was returned as a final code when making the request.

    This will mainly due to the server being uncontactable when making the request.
    """

    pass


class UnexpectedError(APIRequestError):
    """An unexpected error occurred when making the request."""

    pass
