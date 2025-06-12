from fastapi.testclient import TestClient
import pytest
from unittest.mock import Mock

from src.emgmt.database import get_db
from src.emgmt.main import app

mock_session = Mock()


def get_mock_session():
    yield mock_session


app.dependency_overrides[get_db] = get_mock_session


@pytest.fixture
def fake_session():
    return mock_session


@pytest.fixture
def test_client():
    return TestClient(app)
