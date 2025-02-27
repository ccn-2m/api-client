from enum import IntEnum, unique
from json import JSONDecodeError

from rest_api_client_toolkit import APIClient, endpoint, paginated, retry_request
from rest_api_client_toolkit.error_handlers import ErrorHandler
from rest_api_client_toolkit.exceptions import APIRequestError
from rest_api_client_toolkit.response import Response


def by_query_params_callable(response, prev_params):
    if "nextPage" in response and response["nextPage"]:
        return {"page": response["nextPage"]}


class InternalError(APIRequestError):
    message = "Internal error."


class OtherError(APIRequestError):
    message = "Other error."


@unique
class ErrorCodes(IntEnum):
    INTERNAL_ERROR = 20001
    OTHER_ERROR = 20002


ERROR_CODES_WITH_EXCEPTIONS_MAP = {
    ErrorCodes.INTERNAL_ERROR: InternalError,
    ErrorCodes.OTHER_ERROR: OtherError,
}


class ClientErrorHandler(ErrorHandler):
    @staticmethod
    def get_exception(response: Response) -> APIRequestError:
        if response.get_raw_data() == "":
            return ErrorHandler.get_exception(response)

        key_fields = ("errorCode", "error_code")
        error_code = None
        try:
            data = response.get_json()
        except JSONDecodeError:
            return ErrorHandler.get_exception(response)

        for key_field in key_fields:
            try:
                error_code = int(data.get(key_field))
                if error_code is not None:
                    break
            except (ValueError, TypeError):
                pass

        exception_class = ERROR_CODES_WITH_EXCEPTIONS_MAP.get(error_code)
        if not exception_class:
            return ErrorHandler.get_exception(response)

        return exception_class()


@endpoint(base_url="http://testserver")
class Urls:
    users = "users"
    user = "users/{id}"
    accounts = "accounts"


class Client(APIClient):
    def get_request_timeout(self):
        return 0.1

    def list_users(self):
        return self.get(Urls.users)

    @retry_request
    def get_user(self, user_id: int):
        url = Urls.user.format(id=user_id)
        return self.get(url)

    def create_user(self, first_name, last_name):
        data = {"firstName": first_name, "lastName": last_name}
        return self.post(Urls.users, data=data)

    def overwrite_user(self, user_id, first_name, last_name):
        data = {"firstName": first_name, "lastName": last_name}
        url = Urls.user.format(id=user_id)
        return self.put(url, data=data)

    def update_user(self, user_id, first_name=None, last_name=None):
        data = {}
        if first_name:
            data["firstName"] = first_name
        if last_name:
            data["lastName"] = last_name
        url = Urls.user.format(id=user_id)
        return self.patch(url, data=data)

    def delete_user(self, user_id):
        url = Urls.user.format(id=user_id)
        return self.delete(url)

    @paginated(by_query_params=by_query_params_callable)
    def list_user_accounts_paginated(self, user_id):
        return self.get(Urls.accounts, params={"userId": user_id})
