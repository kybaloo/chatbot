"""
Modèle pour les utilisateurs
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class UserPreferences:
    """Préférences personnalisables de l'utilisateur"""
    language: str = "fr"  # Langue préférée (fr, en, etc.)
    response_style: str = "standard"  # Style de réponse (concis, détaillé, standard)
    notifications_enabled: bool = True  # Si les notifications sont activées
    theme: str = "default"  # Thème préféré pour l'interface
    custom_settings: Dict[str, any] = field(default_factory=dict)  # Paramètres personnalisés supplémentaires


@dataclass
class User:
    """Représente un utilisateur du système"""
    user_id: str  # ID Telegram ou autre identifiant
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    conversation_ids: List[str] = field(default_factory=list)  # Liste des IDs de conversation
    preferences: UserPreferences = field(default_factory=UserPreferences)
    tags: List[str] = field(default_factory=list)  # Tags pour catégoriser l'utilisateur
    
    def update_activity(self):
        """Met à jour le timestamp de dernière activité"""
        self.last_activity = datetime.now()
    
    def add_conversation(self, conversation_id: str):
        """Ajoute une conversation à l'utilisateur"""
        if conversation_id not in self.conversation_ids:
            self.conversation_ids.append(conversation_id)
    
    def remove_conversation(self, conversation_id: str):
        """Supprime une conversation de l'utilisateur"""
        if conversation_id in self.conversation_ids:
            self.conversation_ids.remove(conversation_id)
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'conversation_ids': self.conversation_ids,
            'preferences': {
                'language': self.preferences.language,
                'response_style': self.preferences.response_style,
                'notifications_enabled': self.preferences.notifications_enabled,
                'theme': self.preferences.theme,
                'custom_settings': self.preferences.custom_settings
            },
            'tags': self.tags
        }
