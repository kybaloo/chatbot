"""
Repository pour la gestion des conversations dans DynamoDB
"""

import boto3
import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from ..config.settings import env_vars
from ..models import Conversation, Message
from .base_repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """
    Implémentation du repository pour les conversations utilisant DynamoDB
    """

    def __init__(self):
        """Initialisation du repository avec connexion à DynamoDB"""
        self.logger = logging.getLogger(__name__)

        # Utiliser les credentials par défaut sans profil AWS
        try:
            # Forcer l'utilisation des credentials par défaut sans profil
            import os
            # Temporairement supprimer AWS_PROFILE si défini
            old_profile = os.environ.pop('AWS_PROFILE', None)
            
            self.dynamodb = boto3.resource(
                "dynamodb", 
                region_name=env_vars.AWS_REGION_NAME
            )
            
            # Restaurer AWS_PROFILE si c'était défini
            if old_profile:
                os.environ['AWS_PROFILE'] = old_profile
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de la session AWS: {str(e)}")
            # Fallback - utiliser la configuration par défaut
            self.dynamodb = boto3.resource(
                "dynamodb", region_name=env_vars.AWS_REGION_NAME
            )

        self.table = self.dynamodb.Table(env_vars.DYNAMO_TABLE)
        self.logger.info(
            f"ConversationRepository initialized with table {env_vars.DYNAMO_TABLE}"
        )

    def _convert_to_entity(self, item: Dict[str, Any]) -> Conversation:
        """Convertit un item DynamoDB en objet Conversation"""
        if not item:
            return None

        # Créer les objets Message à partir des données JSON
        messages = []
        for msg_data in json.loads(item.get("messages", "[]")):
            messages.append(
                Message(
                    role=msg_data.get("role"),
                    content=msg_data.get("content"),
                    timestamp=datetime.fromisoformat(msg_data.get("timestamp")),
                )
            )

        # Créer et retourner l'objet Conversation
        return Conversation(
            conversation_id=item.get("conversation_id"),
            user_id=item.get("user_id"),
            username=item.get("username"),
            created_at=datetime.fromisoformat(item.get("created_at")),
            updated_at=datetime.fromisoformat(item.get("updated_at")),
            messages=messages,
        )

    def _convert_to_item(self, entity: Conversation) -> Dict[str, Any]:
        """Convertit un objet Conversation en item DynamoDB"""
        # Convertir les messages en format JSON-compatible
        messages_json = []
        for msg in entity.messages:
            messages_json.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
            )

        # Créer l'item DynamoDB
        item = {
            "conversation_id": entity.conversation_id,
            "user_id": entity.user_id,
            "pk": f"USER#{entity.user_id}",
            "sk": f"CONV#{entity.conversation_id}",
            "username": entity.username,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
            "messages": json.dumps(messages_json),
            "message_count": len(entity.messages),
            "ttl": int(
                (
                    datetime.now() + timedelta(days=env_vars.CONVERSATION_TTL_DAYS)
                ).timestamp()
            ),
        }
        return item

    async def get(self, id: str) -> Optional[Conversation]:
        """
        Récupère une conversation par son ID
        Note: Cela nécessite également l'ID utilisateur
        """
        # Cette méthode n'est pas utilisable directement car on a besoin de l'user_id aussi
        # Utiliser get_by_user_and_conversation à la place
        raise NotImplementedError("Use get_by_user_and_conversation instead")

    async def get_by_user_and_conversation(
        self, user_id: str, conversation_id: str
    ) -> Optional[Conversation]:
        """Récupère une conversation spécifique d'un utilisateur"""
        try:
            response = self.table.get_item(
                Key={"pk": f"USER#{user_id}", "sk": f"CONV#{conversation_id}"}
            )
            item = response.get("Item")
            if not item:
                return None

            return self._convert_to_entity(item)
        except Exception as e:
            self.logger.error(
                f"Error getting conversation {conversation_id} for user {user_id}: {str(e)}"
            )
            return None

    async def get_all(self) -> List[Conversation]:
        """Récupère toutes les conversations (attention à la pagination)"""
        # Cette méthode pourrait être très coûteuse sur une grande table
        # Utiliser get_by_user à la place
        raise NotImplementedError("Use get_by_user instead")

    async def get_by_user(self, user_id: str) -> List[Conversation]:
        """Récupère toutes les conversations d'un utilisateur"""
        try:
            response = self.table.query(
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={":pk": f"USER#{user_id}"},
            )

            conversations = []
            for item in response.get("Items", []):
                conversation = self._convert_to_entity(item)
                if conversation:
                    conversations.append(conversation)

            return conversations
        except Exception as e:
            self.logger.error(
                f"Error getting conversations for user {user_id}: {str(e)}"
            )
            return []

    async def create(self, entity: Conversation) -> Conversation:
        """Crée une nouvelle conversation"""
        try:
            item = self._convert_to_item(entity)
            self.table.put_item(Item=item)
            self.logger.info(f"Successfully created conversation {entity.conversation_id} for user {entity.user_id}")
            return entity
        except Exception as e:
            self.logger.error(f"Error creating conversation: {str(e)}")
            raise Exception(f"Failed to create conversation: {str(e)}")

    async def update(self, id: str, entity: Conversation) -> Optional[Conversation]:
        """Met à jour une conversation existante"""
        try:
            # Pour DynamoDB, create et update sont identiques (put_item)
            return await self.create(entity)
        except Exception as e:
            self.logger.error(f"Error updating conversation {id}: {str(e)}")
            return None

    async def delete(self, id: str) -> bool:
        """Supprime une conversation par son ID"""
        # Cette méthode n'est pas implémentable directement car on a besoin de l'user_id aussi
        # Utiliser delete_by_user_and_conversation à la place
        raise NotImplementedError("Use delete_by_user_and_conversation instead")

    async def delete_by_user_and_conversation(
        self, user_id: str, conversation_id: str
    ) -> bool:
        """Supprime une conversation spécifique d'un utilisateur"""
        try:
            self.table.delete_item(
                Key={"pk": f"USER#{user_id}", "sk": f"CONV#{conversation_id}"}
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Error deleting conversation {conversation_id} for user {user_id}: {str(e)}"
            )
            return False

    async def find(self, filter_params: Dict[str, Any]) -> List[Conversation]:
        """Recherche des conversations selon des critères"""
        # Implémentation simplifiée, à adapter selon les besoins
        user_id = filter_params.get("user_id")
        if user_id:
            return await self.get_by_user(user_id)
        return []
