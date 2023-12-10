import pytest
from unittest.mock import patch
from requests.exceptions import ConnectionError
from client import MetadataParserClient
from aiven.client.client import AivenClient

@pytest.fixture
def metadata_parser_client():
    return MetadataParserClient(base_url="https://test.aiven.io", show_http=True, request_timeout=5)

def test_get_service_unhandled_exception(metadata_parser_client):
    # Mock the super().get_service method to raise a RuntimeError
    with patch.object(AivenClient, "get_service", side_effect=RuntimeError):
        with pytest.raises(RuntimeError):
            metadata_parser_client.get_service("test_project", "test_service")

def test_get_service_handled_exceptions(metadata_parser_client, caplog):
    # Mock the super().get_service method to raise a ConnectionError
    with patch.object(AivenClient, "get_service", side_effect=ConnectionError):
        result = metadata_parser_client.get_service("test_project", "test_service")
        assert "Error while getting service: test_service in project: test_project" in caplog.text
        assert result == {}

def test_get_service_no_exception(metadata_parser_client):
    expected_service_data = {'service_name': 'test_service', 'project_name': 'test_project'}
    # Mock the get_service method to return expected data without raising an exception
    with patch.object(metadata_parser_client, 'get_service', return_value=expected_service_data):
        result = metadata_parser_client.get_service("test_project", "test_service")
        assert result == expected_service_data
