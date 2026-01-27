import pytest
from starlette import status
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """
    фикстура для тестового клиента
    """
    with TestClient(app) as test_client:
        yield test_client


def test_create_notification_success(client):
    """
    создание уведомления
    """
    request_data = {
        "user_id": 123,
        "message": "Your code: 11111",
        "type": "telegram"
    }

    # мок фоновой задачи
    with patch('api.notifications.BackgroundTasks') as MockBackgroundTasks:
        mock_tasks = MagicMock()
        MockBackgroundTasks.return_value = mock_tasks

        response = client.post("/api/notifications/", json=request_data)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["user_id"] == 123
    assert response_data["message"] == "Your code: 11111"


def test_create_notification_validation_error(client):
    """
    неверный тип уведомления
    """
    invalid_data = {
        "user_id": 1,
        "message": "Your code: 21321",
        "type": "sms"
    }

    response = client.post("/api/notifications/", json=invalid_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_logical_error_empty_message(client):
    """
    пустое сообщение в уведомлении не имеет смысла и
    должно отклоняться
    """

    response = client.post("/api/notifications/", json={
        "user_id": 1,
        "message": "",
        "type": "telegram"
    })

    assert response.status_code != 201, "пустое сообщение"
