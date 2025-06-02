"""
Tests unitaires pour les modèles de conversation
"""

import pytest
from datetime import datetime, timedelta
from src.models.conversation import Conversation, Message


def test_conversation_creation():
    """Test la création d'un objet Conversation avec des attributs valides"""
    conversation = Conversation(
        conversation_id="test-convo-1",
        user_id="user123",
        title="Test Conversation",
        created_at="2025-06-01T10:00:00Z",
        updated_at="2025-06-01T10:05:00Z",
        messages=[],
        model_id="mistral-medium",
    )

    assert conversation.conversation_id == "test-convo-1"
    assert conversation.user_id == "user123"
    assert conversation.title == "Test Conversation"
    assert conversation.created_at == "2025-06-01T10:00:00Z"
    assert conversation.updated_at == "2025-06-01T10:05:00Z"
    assert conversation.messages == []
    assert conversation.model_id == "mistral-medium"


def test_add_message():
    """Test l'ajout d'un message à une conversation"""
    conversation = Conversation(
        conversation_id="test-convo-1",
        user_id="user123",
        title="Test Conversation",
        created_at="2025-06-01T10:00:00Z",
        updated_at="2025-06-01T10:00:00Z",
        messages=[],
        model_id="mistral-medium",
    )

    # Ajouter un message utilisateur
    conversation.add_message("user", "Bonjour!", "2025-06-01T10:01:00Z")

    assert len(conversation.messages) == 1
    assert conversation.messages[0].role == "user"
    assert conversation.messages[0].content == "Bonjour!"
    assert conversation.messages[0].timestamp == "2025-06-01T10:01:00Z"

    # Ajouter un message assistant
    conversation.add_message(
        "assistant", "Comment puis-je vous aider?", "2025-06-01T10:02:00Z"
    )

    assert len(conversation.messages) == 2
    assert conversation.messages[1].role == "assistant"
    assert conversation.messages[1].content == "Comment puis-je vous aider?"
    assert conversation.messages[1].timestamp == "2025-06-01T10:02:00Z"


def test_to_dict():
    """Test la conversion d'une conversation en dictionnaire"""
    # Créer un message
    message = Message(role="user", content="Bonjour!", timestamp="2025-06-01T10:00:00Z")

    # Créer une conversation avec le message
    conversation = Conversation(
        conversation_id="test-convo-1",
        user_id="user123",
        title="Test Conversation",
        created_at="2025-06-01T10:00:00Z",
        updated_at="2025-06-01T10:05:00Z",
        messages=[message],
        model_id="mistral-medium",
    )

    # Convertir en dictionnaire
    conv_dict = conversation.to_dict()

    # Vérifier le résultat
    assert conv_dict["conversation_id"] == "test-convo-1"
    assert conv_dict["user_id"] == "user123"
    assert conv_dict["title"] == "Test Conversation"
    assert conv_dict["created_at"] == "2025-06-01T10:00:00Z"
    assert conv_dict["updated_at"] == "2025-06-01T10:05:00Z"
    assert len(conv_dict["messages"]) == 1
    assert conv_dict["messages"][0]["role"] == "user"
    assert conv_dict["messages"][0]["content"] == "Bonjour!"
    assert conv_dict["messages"][0]["timestamp"] == "2025-06-01T10:00:00Z"
    assert conv_dict["model_id"] == "mistral-medium"


def test_get_messages_for_mistral():
    """Test la méthode qui formate les messages pour Mistral AI"""
    # Créer une conversation avec plusieurs messages
    conversation = Conversation(
        conversation_id="test-convo-1",
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
            Message(
                role="user",
                content="Peux-tu m'expliquer ce qu'est Python?",
                timestamp="2025-06-01T10:01:00Z",
            ),
        ],
        model_id="mistral-medium",
    )

    # Obtenir les messages formatés pour Mistral
    mistral_messages = conversation.get_messages_for_mistral()

    # Vérifier le résultat
    assert len(mistral_messages) == 3
    assert mistral_messages[0]["role"] == "user"
    assert mistral_messages[0]["content"] == "Bonjour!"
    assert mistral_messages[1]["role"] == "assistant"
    assert mistral_messages[1]["content"] == "Bonjour! Comment puis-je vous aider?"
    assert mistral_messages[2]["role"] == "user"
    assert mistral_messages[2]["content"] == "Peux-tu m'expliquer ce qu'est Python?"

    # Vérifier qu'il n'y a pas de timestamps dans les messages formatés
    assert "timestamp" not in mistral_messages[0]
    assert "timestamp" not in mistral_messages[1]
    assert "timestamp" not in mistral_messages[2]
