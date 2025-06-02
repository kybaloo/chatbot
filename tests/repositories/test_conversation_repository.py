"""
Tests unitaires pour le repository de conversation
"""

import pytest
from unittest.mock import MagicMock, patch
from src.repositories.conversation_repository import ConversationRepository
from src.models.conversation import Conversation, Message


def test_repository_initialization(mock_dynamo_resource, mock_env_vars):
    """Test l'initialisation du repository avec les dépendances nécessaires"""
    repo = ConversationRepository(mock_dynamo_resource, mock_env_vars)

    assert repo.dynamo_resource == mock_dynamo_resource
    assert repo.table_name == mock_env_vars.DYNAMO_TABLE
    assert repo.ttl_days == mock_env_vars.CONVERSATION_TTL_DAYS
    # Vérifier que la table a été récupérée
    mock_dynamo_resource.Table.assert_called_once_with(mock_env_vars.DYNAMO_TABLE)


def test_save_conversation(mock_conversation_repository, sample_conversation):
    """Test la sauvegarde d'une conversation dans DynamoDB"""
    # Configurer le mock pour la table DynamoDB
    mock_table = mock_conversation_repository.dynamo_resource.Table.return_value

    # Appeler la méthode save
    result = mock_conversation_repository.save(sample_conversation)

    # Vérifier que put_item a été appelé avec les bons arguments
    mock_table.put_item.assert_called_once()
    call_args = mock_table.put_item.call_args[1]

    # Vérifier que le dictionnaire Item contient les bonnes valeurs
    assert call_args["Item"]["PK"] == f"USER#{sample_conversation.user_id}"
    assert (
        call_args["Item"]["SK"] == f"CONVERSATION#{sample_conversation.conversation_id}"
    )
    assert call_args["Item"]["conversation_id"] == sample_conversation.conversation_id
    assert call_args["Item"]["user_id"] == sample_conversation.user_id
    assert call_args["Item"]["title"] == sample_conversation.title
    assert call_args["Item"]["created_at"] == sample_conversation.created_at
    assert call_args["Item"]["updated_at"] == sample_conversation.updated_at
    assert call_args["Item"]["model_id"] == sample_conversation.model_id

    # Vérifier que le TTL a été défini
    assert "TTL" in call_args["Item"]

    # Vérifier le résultat retourné
    assert result == sample_conversation


def test_get_conversation_by_id(mock_conversation_repository, sample_conversation):
    """Test la récupération d'une conversation par ID"""
    # Configurer le mock pour la table DynamoDB
    mock_table = mock_conversation_repository.dynamo_resource.Table.return_value

    # Configurer la réponse du mock pour get_item
    mock_table.get_item.return_value = {
        "Item": {
            "PK": f"USER#{sample_conversation.user_id}",
            "SK": f"CONVERSATION#{sample_conversation.conversation_id}",
            "conversation_id": sample_conversation.conversation_id,
            "user_id": sample_conversation.user_id,
            "title": sample_conversation.title,
            "created_at": sample_conversation.created_at,
            "updated_at": sample_conversation.updated_at,
            "model_id": sample_conversation.model_id,
            "messages": [message.to_dict() for message in sample_conversation.messages],
        }
    }

    # Appeler la méthode get_by_id
    result = mock_conversation_repository.get_by_id(
        sample_conversation.user_id, sample_conversation.conversation_id
    )

    # Vérifier que get_item a été appelé avec les bons arguments
    mock_table.get_item.assert_called_once_with(
        Key={
            "PK": f"USER#{sample_conversation.user_id}",
            "SK": f"CONVERSATION#{sample_conversation.conversation_id}",
        }
    )

    # Vérifier que le résultat est une instance de Conversation
    assert isinstance(result, Conversation)
    assert result.conversation_id == sample_conversation.conversation_id
    assert result.user_id == sample_conversation.user_id
    assert result.title == sample_conversation.title
    assert result.created_at == sample_conversation.created_at
    assert result.updated_at == sample_conversation.updated_at
    assert result.model_id == sample_conversation.model_id

    # Vérifier que les messages ont été correctement reconstitués
    assert len(result.messages) == len(sample_conversation.messages)


def test_get_conversation_by_id_not_found(mock_conversation_repository):
    """Test la récupération d'une conversation qui n'existe pas"""
    # Configurer le mock pour la table DynamoDB
    mock_table = mock_conversation_repository.dynamo_resource.Table.return_value

    # Configurer la réponse du mock pour get_item (conversation non trouvée)
    mock_table.get_item.return_value = {}

    # Appeler la méthode get_by_id
    result = mock_conversation_repository.get_by_id("user123", "convo-not-exists")

    # Vérifier que get_item a été appelé
    mock_table.get_item.assert_called_once()

    # Vérifier que le résultat est None
    assert result is None


def test_delete_conversation(mock_conversation_repository, sample_conversation):
    """Test la suppression d'une conversation"""
    # Configurer le mock pour la table DynamoDB
    mock_table = mock_conversation_repository.dynamo_resource.Table.return_value

    # Appeler la méthode delete
    result = mock_conversation_repository.delete(
        sample_conversation.user_id, sample_conversation.conversation_id
    )

    # Vérifier que delete_item a été appelé avec les bons arguments
    mock_table.delete_item.assert_called_once_with(
        Key={
            "PK": f"USER#{sample_conversation.user_id}",
            "SK": f"CONVERSATION#{sample_conversation.conversation_id}",
        }
    )

    # Vérifier que le résultat est True
    assert result is True


def test_list_conversations_for_user(mock_conversation_repository, sample_conversation):
    """Test la récupération de toutes les conversations d'un utilisateur"""
    # Configurer le mock pour la table DynamoDB
    mock_table = mock_conversation_repository.dynamo_resource.Table.return_value

    # Configurer la réponse du mock pour query
    mock_table.query.return_value = {
        "Items": [
            {
                "PK": f"USER#{sample_conversation.user_id}",
                "SK": f"CONVERSATION#{sample_conversation.conversation_id}",
                "conversation_id": sample_conversation.conversation_id,
                "user_id": sample_conversation.user_id,
                "title": sample_conversation.title,
                "created_at": sample_conversation.created_at,
                "updated_at": sample_conversation.updated_at,
                "model_id": sample_conversation.model_id,
                "messages": [
                    message.to_dict() for message in sample_conversation.messages
                ],
            }
        ]
    }

    # Appeler la méthode list_for_user
    result = mock_conversation_repository.list_for_user(sample_conversation.user_id)

    # Vérifier que query a été appelé avec les bons arguments
    mock_table.query.assert_called_once()
    call_args = mock_table.query.call_args[1]
    assert (
        call_args["KeyConditionExpression"].expression
        == "PK = :pk AND begins_with(SK, :sk_prefix)"
    )
    assert (
        call_args["ExpressionAttributeValues"][":pk"]
        == f"USER#{sample_conversation.user_id}"
    )
    assert call_args["ExpressionAttributeValues"][":sk_prefix"] == "CONVERSATION#"

    # Vérifier que le résultat est une liste de Conversation
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Conversation)
    assert result[0].conversation_id == sample_conversation.conversation_id
