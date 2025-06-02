"""
Modèles pour les conversations et messages
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4


@dataclass
class Message:
    """Représente un message dans une conversation"""

    role: str  # 'user' ou 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self):
        """Convertit le message en dictionnaire"""
        return {
            "message_id": self.message_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Conversation:
    """Représente une conversation complète entre un utilisateur et l'assistant"""

    user_id: str
    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    username: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Message] = field(default_factory=list)
    metadata: dict = field(
        default_factory=dict
    )  # Pour stocker des données supplémentaires (tags, titre, etc.)

    def add_message(self, role: str, content: str) -> Message:
        """Ajoute un message à la conversation et met à jour le timestamp"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message

    def clear_messages(self):
        """Efface tous les messages de la conversation"""
        self.messages = []
        self.updated_at = datetime.now()

    def get_last_user_message(self) -> Optional[Message]:
        """Récupère le dernier message de l'utilisateur"""
        for message in reversed(self.messages):
            if message.role == "user":
                return message
        return None

    def get_last_assistant_message(self) -> Optional[Message]:
        """Récupère le dernier message de l'assistant"""
        for message in reversed(self.messages):
            if message.role == "assistant":
                return message
        return None

    def to_dict(self):
        """Convertit la conversation en dictionnaire"""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages],
            "message_count": len(self.messages),
            "metadata": self.metadata,
        }

    def get_messages_for_ai(self):
        """Récupère les messages dans le format attendu par l'API Mistral"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
