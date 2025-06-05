from fastapi.testclient import TestClient

from src.emgmt.main import app

client = TestClient(app)


def test_get_all_request_headers():
    custom_headers = {
        "user-agent": "test-agent",
        "accept-encoding": "gzip, deflate",
        "referer": "http://example.com",
        "accept-language": "en-US,en;q=0.9",
        "connection": "keep-alive",
        "host": "testserver",
    }
    response = client.get("/get_headers", headers=custom_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["User-Agent"] == "test-agent"
    assert data["Accept-Encoding"] == "gzip, deflate"
    assert data["Referer"] == "http://example.com"
    assert data["Accept-Language"] == "en-US,en;q=0.9"
    assert data["Connection"] == "keep-alive"
    assert data["Host"] == "testserver"
