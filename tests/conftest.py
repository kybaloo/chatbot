"""
Configuration des tests pour le projet chatbot
"""

import pytest
import os
import sys
from unittest.mock import MagicMock

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.conversation import Conversation, Message
from src.models.user import User
from src.models.ai_model import AIModel, PREDEFINED_MODELS
from src.repositories.conversation_repository import ConversationRepository
from src.services.conversation_service import ConversationService
from src.services.ai_service import AIService
from src.config.settings import EnvVars


@pytest.fixture
def mock_env_vars():
    """Fixture qui fournit une configuration factice pour les tests"""
    mock_config = MagicMock(spec=EnvVars)
    mock_config.DYNAMO_TABLE = "test-table"
    mock_config.MISTRAL_API_KEY = "test-api-key"
    mock_config.AWS_REGION_NAME = "us-east-1"
    mock_config.CONVERSATION_TTL_DAYS = 30
    mock_config.ENV_NAME = "test"
    mock_config.LOG_LEVEL = "DEBUG"
    mock_config.TELEGRAM_BOT_TOKEN = "test-token"
    return mock_config


@pytest.fixture
def mock_dynamo_resource():
    """Fixture qui fournit un mock de la ressource DynamoDB"""
    mock_resource = MagicMock()
    mock_table = MagicMock()
    mock_resource.Table.return_value = mock_table
    return mock_resource


@pytest.fixture
def mock_conversation_repository(mock_dynamo_resource, mock_env_vars):
    """Fixture qui fournit un repository de conversation mock"""
    repo = ConversationRepository(mock_dynamo_resource, mock_env_vars)
    return repo


@pytest.fixture
def mock_ai_service(mock_env_vars):
    """Fixture qui fournit un service AI mock"""
    service = MagicMock(spec=AIService)
    service.generate_response.return_value = "Ceci est une réponse générée"
    return service


@pytest.fixture
def mock_conversation_service(mock_conversation_repository, mock_ai_service):
    """Fixture qui fournit un service de conversation mock"""
    return ConversationService(mock_conversation_repository, mock_ai_service)


@pytest.fixture
def sample_conversation():
    """Fixture qui fournit un exemple de conversation pour les tests"""
    convo = Conversation(
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
    return convo


@pytest.fixture
def sample_user():
    """Fixture qui fournit un exemple d'utilisateur pour les tests"""
    return User(
        user_id="user123",
        username="testuser",
        first_name="Test",
        last_name="User",
        created_at="2025-06-01T10:00:00Z",
        last_active="2025-06-01T10:05:00Z",
    )
