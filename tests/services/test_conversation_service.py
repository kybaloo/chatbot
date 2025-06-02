"""
Tests unitaires pour le service de conversation
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.services.conversation_service import ConversationService
from src.models.conversation import Conversation, Message


def test_conversation_service_initialization(mock_conversation_repository, mock_ai_service):
    """Test l'initialisation du service de conversation avec ses dépendances"""
    service = ConversationService(mock_conversation_repository, mock_ai_service)
    
    assert service.repository == mock_conversation_repository
    assert service.ai_service == mock_ai_service


def test_create_conversation(mock_conversation_repository, mock_ai_service):
    """Test la création d'une nouvelle conversation"""
    service = ConversationService(mock_conversation_repository, mock_ai_service)
    
    # Configurer le mock pour save
    mock_conversation_repository.save.return_value = MagicMock(spec=Conversation)
    
    # Appeler la méthode create_conversation
    user_id = "user123"
    title = "Nouvelle conversation"
    model_id = "mistral-medium"
    
    conversation = service.create_conversation(user_id, title, model_id)
    
    # Vérifier que save a été appelé
    mock_conversation_repository.save.assert_called_once()
    
    # Vérifier les propriétés de la conversation créée
    saved_conversation = mock_conversation_repository.save.call_args[0][0]
    assert isinstance(saved_conversation, Conversation)
    assert saved_conversation.user_id == user_id
    assert saved_conversation.title == title
    assert saved_conversation.model_id == model_id
    assert saved_conversation.messages == []
    
    # Vérifier qu'un ID a été généré
    assert saved_conversation.conversation_id is not None
    assert len(saved_conversation.conversation_id) > 0
    
    # Vérifier les timestamps
    assert saved_conversation.created_at is not None
    assert saved_conversation.updated_at is not None


def test_get_conversation(mock_conversation_repository, mock_ai_service, sample_conversation):
    """Test la récupération d'une conversation par ID"""
    service = ConversationService(mock_conversation_repository, mock_ai_service)
    
    # Configurer le mock pour get_by_id
    mock_conversation_repository.get_by_id.return_value = sample_conversation
    
    # Appeler la méthode get_conversation
    conversation = service.get_conversation(sample_conversation.user_id, sample_conversation.conversation_id)
    
    # Vérifier que get_by_id a été appelé avec les bons arguments
    mock_conversation_repository.get_by_id.assert_called_once_with(
        sample_conversation.user_id, sample_conversation.conversation_id
    )
    
    # Vérifier que la conversation retournée est correcte
    assert conversation == sample_conversation


def test_get_conversation_not_found(mock_conversation_repository, mock_ai_service):
    """Test la récupération d'une conversation qui n'existe pas"""
    service = ConversationService(mock_conversation_repository, mock_ai_service)
    
    # Configurer le mock pour get_by_id
    mock_conversation_repository.get_by_id.return_value = None
    
    # Appeler la méthode get_conversation
    conversation = service.get_conversation("user123", "convo-not-exists")
    
    # Vérifier que get_by_id a été appelé
    mock_conversation_repository.get_by_id.assert_called_once()
    
    # Vérifier que None est retourné
    assert conversation is None


def test_add_user_message_and_get_ai_response(mock_conversation_repository, mock_ai_service, sample_conversation):
    """Test l'ajout d'un message utilisateur et l'obtention d'une réponse de l'IA"""
    service = ConversationService(mock_conversation_repository, mock_ai_service)
    
    # Faire une copie de la conversation d'exemple pour éviter de la modifier
    conversation = Conversation(
        conversation_id=sample_conversation.conversation_id,
        user_id=sample_conversation.user_id,
        title=sample_conversation.title,
        created_at=sample_conversation.created_at,
        updated_at=sample_conversation.updated_at,
        messages=sample_conversation.messages.copy(),
        model_id=sample_conversation.model_id
    )
    
    # Configurer les mocks
    mock_conversation_repository.get_by_id.return_value = conversation
    mock_conversation_repository.save.return_value = conversation
    mock_ai_service.generate_response.return_value = "Voici la réponse de l'IA à votre question."
    
    # Appeler la méthode add_user_message_and_get_ai_response
    user_message = "Quelle est la capitale de la France?"
    ai_response = service.add_user_message_and_get_ai_response(
        conversation.user_id, conversation.conversation_id, user_message
    )
    
    # Vérifier que get_by_id a été appelé
    mock_conversation_repository.get_by_id.assert_called_once_with(
        conversation.user_id, conversation.conversation_id
    )
    
    # Vérifier que le message utilisateur a été ajouté
    assert len(conversation.messages) > len(sample_conversation.messages)
    last_user_message = conversation.messages[-2]  # L'avant-dernier message devrait être celui de l'utilisateur
    assert last_user_message.role == "user"
    assert last_user_message.content == user_message
    
    # Vérifier que le message de l'IA a été ajouté
    last_ai_message = conversation.messages[-1]  # Le dernier message devrait être celui de l'IA
    assert last_ai_message.role == "assistant"
    assert last_ai_message.content == "Voici la réponse de l'IA à votre question."
    
    # Vérifier que generate_response a été appelé avec les bons messages
    mock_ai_service.generate_response.assert_called_once()
    messages_for_ai = mock_ai_service.generate_response.call_args[0][0]
    assert isinstance(messages_for_ai, list)
    
    # Vérifier que save a été appelé pour sauvegarder la conversation mise à jour
    mock_conversation_repository.save.assert_called_once_with(conversation)
    
    # Vérifier que la réponse de l'IA est retournée
    assert ai_response == "Voici la réponse de l'IA à votre question."


def test_list_conversations(mock_conversation_repository, mock_ai_service, sample_conversation):
    """Test la récupération de toutes les conversations d'un utilisateur"""
    service = ConversationService(mock_conversation_repository, mock_ai_service)
    
    # Configurer le mock pour list_for_user
    mock_conversation_repository.list_for_user.return_value = [sample_conversation]
    
    # Appeler la méthode list_conversations
    conversations = service.list_conversations(sample_conversation.user_id)
    
    # Vérifier que list_for_user a été appelé avec le bon argument
    mock_conversation_repository.list_for_user.assert_called_once_with(sample_conversation.user_id)
    
    # Vérifier que la liste retournée est correcte
    assert len(conversations) == 1
    assert conversations[0] == sample_conversation


def test_delete_conversation(mock_conversation_repository, mock_ai_service, sample_conversation):
    """Test la suppression d'une conversation"""
    service = ConversationService(mock_conversation_repository, mock_ai_service)
    
    # Configurer le mock pour delete
    mock_conversation_repository.delete.return_value = True
    
    # Appeler la méthode delete_conversation
    result = service.delete_conversation(sample_conversation.user_id, sample_conversation.conversation_id)
    
    # Vérifier que delete a été appelé avec les bons arguments
    mock_conversation_repository.delete.assert_called_once_with(
        sample_conversation.user_id, sample_conversation.conversation_id
    )
    
    # Vérifier que le résultat est correct
    assert result is True


def test_update_conversation_title(mock_conversation_repository, mock_ai_service, sample_conversation):
    """Test la mise à jour du titre d'une conversation"""
    service = ConversationService(mock_conversation_repository, mock_ai_service)
    
    # Faire une copie de la conversation d'exemple pour éviter de la modifier
    conversation = Conversation(
        conversation_id=sample_conversation.conversation_id,
        user_id=sample_conversation.user_id,
        title=sample_conversation.title,
        created_at=sample_conversation.created_at,
        updated_at=sample_conversation.updated_at,
        messages=sample_conversation.messages.copy(),
        model_id=sample_conversation.model_id
    )
    
    # Configurer les mocks
    mock_conversation_repository.get_by_id.return_value = conversation
    mock_conversation_repository.save.return_value = conversation
    
    # Appeler la méthode update_conversation_title
    new_title = "Nouveau titre de conversation"
    updated_conversation = service.update_conversation_title(
        conversation.user_id, conversation.conversation_id, new_title
    )
    
    # Vérifier que get_by_id a été appelé
    mock_conversation_repository.get_by_id.assert_called_once_with(
        conversation.user_id, conversation.conversation_id
    )
    
    # Vérifier que le titre a été mis à jour
    assert conversation.title == new_title
    
    # Vérifier que save a été appelé pour sauvegarder la conversation mise à jour
    mock_conversation_repository.save.assert_called_once_with(conversation)
    
    # Vérifier que la conversation mise à jour est retournée
    assert updated_conversation == conversation
