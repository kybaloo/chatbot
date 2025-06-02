"""
Tests d'intégration pour l'API FastAPI
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import json

from src.api.routes import router
from src.models.conversation import Conversation, Message
from src.services.conversation_service import ConversationService


@pytest.fixture
def test_app():
    """Fixture qui configure l'application de test avec des mocks pour les services"""
    from fastapi import FastAPI

    # Créer des mocks pour les services
    mock_conversation_service = MagicMock(spec=ConversationService)

    # Créer une application FastAPI de test
    app = FastAPI()

    # Configurer les dépendances
    async def get_conversation_service():
        return mock_conversation_service

    # Remplacer les dépendances dans le router
    app.dependency_overrides = {
        router.get_conversation_service: get_conversation_service
    }

    # Inclure le router
    app.include_router(router)

    # Créer un client de test
    client = TestClient(app)

    # Retourner le client et les mocks
    return {"client": client, "mock_conversation_service": mock_conversation_service}


def test_create_conversation(test_app):
    """Test la création d'une conversation via l'API"""
    client = test_app["client"]
    mock_conversation_service = test_app["mock_conversation_service"]

    # Configurer le mock pour create_conversation
    mock_conversation = Conversation(
        conversation_id="test-convo-123",
        user_id="user123",
        title="Test Conversation",
        created_at="2025-06-01T10:00:00Z",
        updated_at="2025-06-01T10:00:00Z",
        messages=[],
        model_id="mistral-medium",
    )
    mock_conversation_service.create_conversation.return_value = mock_conversation

    # Faire une requête POST à l'endpoint
    response = client.post(
        "/conversations",
        json={
            "user_id": "user123",
            "title": "Test Conversation",
            "model_id": "mistral-medium",
        },
    )

    # Vérifier la réponse
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["conversation_id"] == mock_conversation.conversation_id
    assert response_data["user_id"] == mock_conversation.user_id
    assert response_data["title"] == mock_conversation.title

    # Vérifier que le service a été appelé avec les bons arguments
    mock_conversation_service.create_conversation.assert_called_once_with(
        "user123", "Test Conversation", "mistral-medium"
    )


def test_get_conversation(test_app):
    """Test la récupération d'une conversation via l'API"""
    client = test_app["client"]
    mock_conversation_service = test_app["mock_conversation_service"]

    # Configurer le mock pour get_conversation
    mock_conversation = Conversation(
        conversation_id="test-convo-123",
        user_id="user123",
        title="Test Conversation",
        created_at="2025-06-01T10:00:00Z",
        updated_at="2025-06-01T10:05:00Z",
        messages=[
            Message(role="user", content="Bonjour!", timestamp="2025-06-01T10:00:00Z"),
            Message(
                role="assistant",
                content="Bonjour! Comment puis-je vous aider?",
                timestamp="2025-06-01T10:00:05Z",
            ),
        ],
        model_id="mistral-medium",
    )
    mock_conversation_service.get_conversation.return_value = mock_conversation

    # Faire une requête GET à l'endpoint
    response = client.get("/conversations/user123/test-convo-123")

    # Vérifier la réponse
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["conversation_id"] == mock_conversation.conversation_id
    assert response_data["user_id"] == mock_conversation.user_id
    assert response_data["title"] == mock_conversation.title
    assert len(response_data["messages"]) == 2

    # Vérifier que le service a été appelé avec les bons arguments
    mock_conversation_service.get_conversation.assert_called_once_with(
        "user123", "test-convo-123"
    )


def test_get_conversation_not_found(test_app):
    """Test la récupération d'une conversation qui n'existe pas"""
    client = test_app["client"]
    mock_conversation_service = test_app["mock_conversation_service"]

    # Configurer le mock pour get_conversation (conversation non trouvée)
    mock_conversation_service.get_conversation.return_value = None

    # Faire une requête GET à l'endpoint
    response = client.get("/conversations/user123/convo-not-exists")

    # Vérifier la réponse
    assert response.status_code == 404

    # Vérifier que le service a été appelé
    mock_conversation_service.get_conversation.assert_called_once()


def test_list_conversations(test_app):
    """Test la récupération de toutes les conversations d'un utilisateur"""
    client = test_app["client"]
    mock_conversation_service = test_app["mock_conversation_service"]

    # Configurer le mock pour list_conversations
    mock_conversations = [
        Conversation(
            conversation_id="test-convo-1",
            user_id="user123",
            title="Conversation 1",
            created_at="2025-06-01T10:00:00Z",
            updated_at="2025-06-01T10:05:00Z",
            messages=[],
            model_id="mistral-medium",
        ),
        Conversation(
            conversation_id="test-convo-2",
            user_id="user123",
            title="Conversation 2",
            created_at="2025-06-01T11:00:00Z",
            updated_at="2025-06-01T11:05:00Z",
            messages=[],
            model_id="mistral-medium",
        ),
    ]
    mock_conversation_service.list_conversations.return_value = mock_conversations

    # Faire une requête GET à l'endpoint
    response = client.get("/conversations/user123")

    # Vérifier la réponse
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 2
    assert response_data[0]["conversation_id"] == mock_conversations[0].conversation_id
    assert response_data[1]["conversation_id"] == mock_conversations[1].conversation_id

    # Vérifier que le service a été appelé avec le bon argument
    mock_conversation_service.list_conversations.assert_called_once_with("user123")


def test_add_message(test_app):
    """Test l'ajout d'un message à une conversation et l'obtention d'une réponse de l'IA"""
    client = test_app["client"]
    mock_conversation_service = test_app["mock_conversation_service"]

    # Configurer le mock pour add_user_message_and_get_ai_response
    ai_response = "Voici la réponse de l'IA à votre question."
    mock_conversation_service.add_user_message_and_get_ai_response.return_value = (
        ai_response
    )

    # Faire une requête POST à l'endpoint
    response = client.post(
        "/conversations/user123/test-convo-123/messages",
        json={"content": "Quelle est la capitale de la France?"},
    )

    # Vérifier la réponse
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["ai_response"] == ai_response

    # Vérifier que le service a été appelé avec les bons arguments
    mock_conversation_service.add_user_message_and_get_ai_response.assert_called_once_with(
        "user123", "test-convo-123", "Quelle est la capitale de la France?"
    )


def test_delete_conversation(test_app):
    """Test la suppression d'une conversation"""
    client = test_app["client"]
    mock_conversation_service = test_app["mock_conversation_service"]

    # Configurer le mock pour delete_conversation
    mock_conversation_service.delete_conversation.return_value = True

    # Faire une requête DELETE à l'endpoint
    response = client.delete("/conversations/user123/test-convo-123")

    # Vérifier la réponse
    assert response.status_code == 204

    # Vérifier que le service a été appelé avec les bons arguments
    mock_conversation_service.delete_conversation.assert_called_once_with(
        "user123", "test-convo-123"
    )
