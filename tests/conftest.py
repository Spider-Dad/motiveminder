"""
Common test fixtures and configuration
"""
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_response():
    """Mock для ответа requests"""
    response = Mock()
    response.raise_for_status = Mock()
    return response

@pytest.fixture
def mock_requests(mocker):
    """Mock для библиотеки requests"""
    return mocker.patch('requests.post') 