"""
Service pour la gestion des conversations
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from ..models import Conversation, Message
from ..repositories.conversation_repository import ConversationRepository
from .base_service import BaseService


class ConversationService(BaseService[Conversation]):
    """
    Service pour gérer les conversations
    Implémente la logique métier pour les conversations
    """

    def __init__(self, repository: Optional[ConversationRepository] = None):
        """Initialisation du service avec son repository"""
        self.logger = logging.getLogger(__name__)
        self.repository = repository or ConversationRepository()

    async def get(self, id: str) -> Optional[Conversation]:
        """Récupère une conversation par son ID (non implémenté)"""
        # Cette méthode n'est pas utilisable directement car on a besoin de l'user_id aussi
        # Utiliser get_by_user_and_conversation à la place
        raise NotImplementedError("Use get_by_user_and_conversation instead")

    async def get_by_user_and_conversation(
        self, user_id: str, conversation_id: str
    ) -> Optional[Conversation]:
        """Récupère une conversation spécifique d'un utilisateur"""
        return await self.repository.get_by_user_and_conversation(
            user_id, conversation_id
        )

    async def get_all(self) -> List[Conversation]:
        """Récupère toutes les conversations (non implémenté)"""
        # Cette méthode pourrait être très coûteuse sur une grande table
        # Utiliser get_by_user à la place
        raise NotImplementedError("Use get_by_user instead")

    async def get_by_user(self, user_id: str) -> List[Conversation]:
        """Récupère toutes les conversations d'un utilisateur"""
        return await self.repository.get_by_user(user_id)

    async def create(self, entity: Conversation) -> Conversation:
        """Crée une nouvelle conversation"""
        return await self.repository.create(entity)

    async def create_new_conversation(
        self, user_id: str, username: Optional[str] = None
    ) -> Conversation:
        """Crée une nouvelle conversation pour un utilisateur"""
        conversation = Conversation(
            user_id=user_id,
            username=username,
            conversation_id=str(uuid4()),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return await self.create(conversation)

    async def update(self, id: str, entity: Conversation) -> Optional[Conversation]:
        """Met à jour une conversation existante"""
        return await self.repository.update(id, entity)

    async def delete(self, id: str) -> bool:
        """Supprime une conversation par son ID (non implémenté)"""
        # Cette méthode n'est pas implémentable directement car on a besoin de l'user_id aussi
        # Utiliser delete_by_user_and_conversation à la place
        raise NotImplementedError("Use delete_by_user_and_conversation instead")

    async def delete_by_user_and_conversation(
        self, user_id: str, conversation_id: str
    ) -> bool:
        """Supprime une conversation spécifique d'un utilisateur"""
        return await self.repository.delete_by_user_and_conversation(
            user_id, conversation_id
        )

    async def add_message(
        self, conversation: Conversation, role: str, content: str
    ) -> Conversation:
        """Ajoute un message à une conversation et la sauvegarde"""
        conversation.add_message(role=role, content=content)
        return await self.update(conversation.conversation_id, conversation)

    async def clear_conversation_history(
        self, user_id: str, conversation_id: str
    ) -> Optional[Conversation]:
        """Efface l'historique d'une conversation"""
        conversation = await self.get_by_user_and_conversation(user_id, conversation_id)
        if not conversation:
            return None

        conversation.clear_messages()
        return await self.update(conversation_id, conversation)

    async def archive_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Archive une conversation (marque comme archivée sans la supprimer)"""
        conversation = await self.get_by_user_and_conversation(user_id, conversation_id)
        if not conversation:
            return False

        # Ajouter métadonnées d'archivage
        conversation.metadata["archived"] = True
        conversation.metadata["archived_at"] = datetime.now().isoformat()

        # Mettre à jour la conversation
        await self.update(conversation_id, conversation)
        return True

    async def rename_conversation(
        self, user_id: str, conversation_id: str, new_title: str
    ) -> Optional[Conversation]:
        """Renomme une conversation"""
        conversation = await self.get_by_user_and_conversation(user_id, conversation_id)
        if not conversation:
            return None

        # Mettre à jour le titre dans les métadonnées
        conversation.metadata["title"] = new_title

        # Mettre à jour la conversation
        return await self.update(conversation_id, conversation)

    def get_formatted_history(
        self, conversation: Conversation, max_messages: int = 5
    ) -> str:
        """Récupère un historique formaté d'une conversation pour affichage"""
        if not conversation or not conversation.messages:
            return "Aucun message dans cette conversation."

        # Limite du nombre de messages à afficher
        messages = (
            conversation.messages[-max_messages:]
            if len(conversation.messages) > max_messages
            else conversation.messages
        )

        # Formatage de l'historique
        history = []
        for msg in messages:
            role_display = "Vous" if msg.role == "user" else "Assistant"
            content_preview = (
                msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            )
            history.append(f"{role_display}: {content_preview}")

        # Informations sur les messages non affichés
        if len(conversation.messages) > max_messages:
            remaining = len(conversation.messages) - max_messages
            history.insert(0, f"... et {remaining} autres messages précédents ...")

        return "\n".join(history)
