import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from message_builder.api import app

@pytest.fixture
def mock_publisher():
    with patch("message_builder.api.pubsub_v1.PublisherClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_future = MagicMock()
        mock_future.result.return_value = "msg123"
        mock_client.publish.return_value = mock_future
        
        yield mock_client

@pytest.fixture
def client(mock_publisher):
    with TestClient(app) as c:
        yield c, mock_publisher

def test_publish_teletype(client):
    test_client, mock_publish = client
    
    payload = {
        "destination": "LHRXXBA",
        "origin": "JFKYYBA",
        "tag": "TESTTAG",
        "body": "HELLO WORLD"
    }

    response = test_client.post("/messages/teletype", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["message_id"] == "msg123"
    assert data["ordering_key"] == "LHRXXBA" 

    # Verify publish called
    mock_publish.publish.assert_called_once()
    args, kwargs = mock_publish.publish.call_args
    assert kwargs.get("ordering_key") == "LHRXXBA"

def test_publish_with_custom_ordering_key(client):
    test_client, mock_publish = client
    
    payload = {
        "destination": "LHRXXBA",
        "origin": "JFKYYBA",
        "body": "HELLO WORLD",
        "ordering_key": "CUSTOM_KEY"
    }

    response = test_client.post("/messages/teletype", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ordering_key"] == "CUSTOM_KEY"
