import json
from unittest.mock import sentinel
from xml.etree import ElementTree

import pytest

from rest_api_client_toolkit import JsonResponseHandler, RequestsResponseHandler, XmlResponseHandler
from rest_api_client_toolkit.exceptions import ResponseParseError
from rest_api_client_toolkit.response import RequestsResponse
from rest_api_client_toolkit.response_handlers import BaseResponseHandler
from tests.helpers import build_response


@pytest.fixture
def blank_response():
    """Fixture that constructs a response with a blank body."""
    return build_response(data="")


class TestBaseResponseHandler:
    handler = BaseResponseHandler

    def test_get_request_data_needs_implementation(self):
        with pytest.raises(NotImplementedError):
            self.handler.get_request_data(sentinel.response)


class TestRequestsResponseHandler:
    handler = RequestsResponseHandler

    def test_original_response_is_returned(self):
        data = self.handler.get_request_data(RequestsResponse(sentinel.response))
        assert data == sentinel.response


class TestJsonResponseHandler:
    handler = JsonResponseHandler

    def test_response_json_is_parsed_correctly(self):
        response = build_response(data=json.dumps({"foo": "bar"}))
        data = self.handler.get_request_data(response)
        assert data == {"foo": "bar"}

    def test_bad_json_raises_response_parse_error(self):
        response = build_response(data="foo")
        with pytest.raises(ResponseParseError) as exc_info:
            self.handler.get_request_data(response)
        assert str(exc_info.value) == "Unable to decode response data to json. data='foo'"

    def test_blank_response_body_returns_none(self, blank_response):
        data = self.handler.get_request_data(blank_response)
        assert data is None


class TestXmlResponseHandler:
    handler = XmlResponseHandler

    def test_response_data_is_parsed_correctly(self):
        response = build_response(data='<?xml version="1.0"?><xml><title>Test Title</title></xml>')
        data = self.handler.get_request_data(response)
        assert isinstance(data, ElementTree.Element)
        assert data.tag == "xml"
        assert data[0].tag == "title"
        assert data[0].text == "Test Title"

    def test_bad_xml_raises_response_parse_error(self):
        response = build_response(data="foo")
        with pytest.raises(ResponseParseError) as exc_info:
            self.handler.get_request_data(response)
        assert str(exc_info.value) == "Unable to parse response data to xml. data='foo'"

    def test_blank_response_body_returns_none(self, blank_response):
        data = self.handler.get_request_data(blank_response)
        assert data is None
