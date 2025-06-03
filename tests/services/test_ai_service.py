"""
Tests unitaires pour le service AI
"""

import pytest
from unittest.mock import MagicMock, patch
from src.services.ai_service import AIService
from src.models.ai_model import AIModel, PREDEFINED_MODELS


@pytest.fixture
def mock_mistral_client():
    """Fixture qui fournit un mock du client Mistral AI"""
    mock_client = MagicMock()
    mock_chat_response = MagicMock()
    mock_chat_response.choices = [MagicMock()]
    mock_chat_response.choices[0].message.content = "Voici une réponse générée par l'IA"
    mock_client.chat.completions.create.return_value = mock_chat_response
    return mock_client


@pytest.fixture
def ai_service(mock_env_vars, mock_mistral_client):
    """Fixture qui fournit une instance du service AI avec un client mock"""
    with patch(
        "src.services.ai_service.MistralClient", return_value=mock_mistral_client
    ):
        service = AIService(mock_env_vars)
        service.client = mock_mistral_client
        return service


def test_ai_service_initialization(mock_env_vars):
    """Test l'initialisation du service AI avec la configuration"""
    with patch("src.services.ai_service.MistralClient") as mock_client_class:
        service = AIService(mock_env_vars)

        # Vérifier que le client Mistral a été initialisé avec la bonne clé API
        mock_client_class.assert_called_once_with(api_key=mock_env_vars.MISTRAL_API_KEY)

        # Vérifier que le modèle par défaut est configuré
        assert service.default_model_id == "mistral-medium"

        # Vérifier que les paramètres par défaut sont configurés
        assert service.default_parameters == {
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1.0,
        }


def test_generate_response(ai_service):
    """Test la génération d'une réponse à partir de messages"""
    # Préparer les messages de test
    messages = [
        {"role": "user", "content": "Bonjour!"},
        {"role": "assistant", "content": "Bonjour! Comment puis-je vous aider?"},
        {"role": "user", "content": "Qu'est-ce que Python?"},
    ]

    # Appeler la méthode generate_response
    response = ai_service.generate_response(messages)

    # Vérifier que le client Mistral a été appelé avec les bons arguments
    ai_service.client.chat.completions.create.assert_called_once()
    call_args = ai_service.client.chat.completions.create.call_args[1]

    assert call_args["model"] == "mistral-medium"
    assert call_args["messages"] == messages
    assert call_args["temperature"] == 0.7
    assert call_args["max_tokens"] == 1024
    assert call_args["top_p"] == 1.0

    # Vérifier que la réponse est correcte
    assert response == "Voici une réponse générée par l'IA"


def test_generate_response_with_custom_model(ai_service):
    """Test la génération d'une réponse avec un modèle personnalisé"""
    # Préparer les messages de test
    messages = [
        {"role": "user", "content": "Bonjour!"},
        {"role": "assistant", "content": "Bonjour! Comment puis-je vous aider?"},
        {
            "role": "user",
            "content": "Explique-moi la physique quantique en termes simples",
        },
    ]

    # Modèle personnalisé
    model_id = "mistral-large"

    # Appeler la méthode generate_response avec un modèle personnalisé
    response = ai_service.generate_response(messages, model_id=model_id)

    # Vérifier que le client Mistral a été appelé avec les bons arguments
    call_args = ai_service.client.chat.completions.create.call_args[1]
    assert call_args["model"] == model_id

    # Vérifier que la réponse est correcte
    assert response == "Voici une réponse générée par l'IA"


def test_generate_response_with_custom_parameters(ai_service):
    """Test la génération d'une réponse avec des paramètres personnalisés"""
    # Préparer les messages de test
    messages = [
        {"role": "user", "content": "Bonjour!"},
        {"role": "assistant", "content": "Bonjour! Comment puis-je vous aider?"},
        {
            "role": "user",
            "content": "Écris-moi un poème sur l'intelligence artificielle",
        },
    ]

    # Paramètres personnalisés
    params = {"temperature": 0.9, "max_tokens": 2048, "top_p": 0.95}

    # Appeler la méthode generate_response avec des paramètres personnalisés
    response = ai_service.generate_response(messages, parameters=params)

    # Vérifier que le client Mistral a été appelé avec les bons arguments
    call_args = ai_service.client.chat.completions.create.call_args[1]
    assert call_args["temperature"] == params["temperature"]
    assert call_args["max_tokens"] == params["max_tokens"]
    assert call_args["top_p"] == params["top_p"]

    # Vérifier que la réponse est correcte
    assert response == "Voici une réponse générée par l'IA"


def test_get_model_by_id():
    """Test la récupération d'un modèle par son ID"""
    # Tester avec un ID valide
    model = AIService.get_model_by_id("mistral-medium")

    assert isinstance(model, AIModel)
    assert model.id == "mistral-medium"
    assert model.name == "Mistral Medium"

    # Tester avec un ID invalide
    model = AIService.get_model_by_id("modele-inexistant")

    assert model is None
