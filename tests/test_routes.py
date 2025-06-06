from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

# from tests.testconf import test_client, fake_session


def test_get_all_request_headers(test_client):
    custom_headers = {
        "user-agent": "test-agent",
        "accept-encoding": "gzip, deflate",
        "referer": "http://example.com",
        "accept-language": "en-US,en;q=0.9",
        "connection": "keep-alive",
        "host": "testserver",
    }
    response = test_client.get("/get_headers", headers=custom_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["User-Agent"] == "test-agent"
    assert data["Accept-Encoding"] == "gzip, deflate"
    assert data["Referer"] == "http://example.com"
    assert data["Accept-Language"] == "en-US,en;q=0.9"
    assert data["Connection"] == "keep-alive"
    assert data["Host"] == "testserver"


def test_display_employees(test_client, fake_session):
    # Mock the chained SQLAlchemy calls: execute().scalars().all()
    fake_employees = [
        {
            "id": uuid4(),
            "name": "E1",
            "age": 20,
            "username": "e1",
            "email": "e1@xyz.com",
            "salary": Decimal("1000"),
        },
        {
            "id": uuid4(),
            "name": "E2",
            "age": 30,
            "username": "e2",
            "email": "e2@xyz.com",
            "salary": Decimal("2000"),
        },
        {
            "id": uuid4(),
            "name": "E3",
            "age": 40,
            "username": "e3",
            "email": "e3@xyz.com",
            "salary": Decimal("3000"),
        },
        {
            "id": uuid4(),
            "name": "E4",
            "age": 50,
            "username": "e4",
            "email": "e4@xyz.com",
            "salary": Decimal("4000"),
        },
        {
            "id": uuid4(),
            "name": "E5",
            "age": 60,
            "username": "e5",
            "email": "e5@xyz.com",
            "salary": Decimal("5000"),
        },
    ]

    mock_execute = Mock()
    mock_scalars = Mock()
    mock_scalars.all.return_value = fake_employees
    mock_execute.scalars.return_value = mock_scalars
    fake_session.execute.return_value = mock_execute

    response = test_client.get("/employees/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert data[2]["name"] == "E3"
    assert Decimal(data[4]["salary"]) == Decimal("5000")
