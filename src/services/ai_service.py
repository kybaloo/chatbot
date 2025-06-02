"""
Service pour l'intégration avec les modèles d'IA
"""

import logging
from typing import List, Dict, Optional, Any
from mistralai import Mistral
from mistralai.exceptions import MistralException

from ..config.settings import env_vars
from ..models import Conversation, AIModel
from ..models.ai_model import MISTRAL_MODELS


class AIService:
    """
    Service pour interagir avec les API d'IA
    Gère l'intégration avec Mistral AI et potentiellement d'autres fournisseurs
    """

    def __init__(self, model_id: str = "mistral-small-latest"):
        """Initialise le service avec un modèle spécifique"""
        self.logger = logging.getLogger(__name__)
        self.api_key = env_vars.MISTRAL_API_KEY
        self.model_id = model_id
        self.model_config = MISTRAL_MODELS.get(
            model_id.split("-")[0] + "-" + model_id.split("-")[1],
            MISTRAL_MODELS["mistral-small"],
        )

        # Initialiser le client Mistral
        self.client = Mistral(api_key=self.api_key)
        self.logger.info(f"AIService initialized with model {model_id}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
    ) -> Dict[str, Any]:
        """
        Obtient une complétion de chat à partir de l'API Mistral

        Args:
            messages: Liste de messages au format [{"role": "user", "content": "Hello"}, ...]
            temperature: Contrôle la créativité (0.0 à 1.0)
            max_tokens: Nombre maximum de tokens en sortie

        Returns:
            Dictionnaire contenant la réponse
        """
        try:
            # Utiliser les paramètres par défaut du modèle si non spécifiés
            params = {}
            if temperature is not None:
                params["temperature"] = temperature
            else:
                params["temperature"] = self.model_config.model_parameters.get(
                    "temperature", 0.7
                )

            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            else:
                params["max_tokens"] = self.model_config.max_tokens

            # Appeler l'API Mistral
            response = self.client.chat.complete(
                model=self.model_id, messages=messages, **params
            )

            # Extraire et formater la réponse
            result = {
                "id": response.id,
                "model": response.model,
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
            }

            return result

        except MistralException as e:
            self.logger.error(f"Mistral API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error in chat completion: {str(e)}")
            raise

    async def process_conversation(self, conversation: Conversation) -> Optional[str]:
        """
        Traite une conversation entière et obtient une réponse

        Args:
            conversation: Objet Conversation contenant l'historique des messages

        Returns:
            Contenu de la réponse du modèle
        """
        try:
            # Convertir les messages de la conversation au format attendu par l'API
            messages = conversation.get_messages_for_ai()

            if not messages:
                return None

            # Obtenir la complétion
            result = await self.chat_completion(messages)

            return result["content"]

        except Exception as e:
            self.logger.error(f"Error processing conversation: {str(e)}")
            return None

    async def simple_query(self, query: str) -> Optional[str]:
        """
        Effectue une requête simple sans contexte de conversation

        Args:
            query: Question ou instruction pour le modèle

        Returns:
            Réponse du modèle
        """
        try:
            messages = [{"role": "user", "content": query}]
            result = await self.chat_completion(messages)
            return result["content"]
        except Exception as e:
            self.logger.error(f"Error in simple query: {str(e)}")
            return None

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des modèles disponibles

        Returns:
            Liste des modèles avec leurs caractéristiques
        """
        return [model.to_dict() for model in MISTRAL_MODELS.values()]

    def switch_model(self, model_id: str) -> bool:
        """
        Change le modèle utilisé par le service

        Args:
            model_id: Identifiant du nouveau modèle

        Returns:
            True si le changement a réussi, False sinon
        """
        model_key = model_id.split("-")[0] + "-" + model_id.split("-")[1]
        if model_key not in MISTRAL_MODELS:
            self.logger.error(f"Model {model_id} not found")
            return False

        self.model_id = model_id
        self.model_config = MISTRAL_MODELS[model_key]
        self.logger.info(f"Switched to model {model_id}")
        return True
