"""
Fonctions utilitaires diverses pour l'application
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio

from ..models import Conversation
from .logger import log_info, log_error


def generate_unique_id() -> str:
    """Génère un identifiant unique"""
    return str(uuid.uuid4())


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formate une date en chaîne de caractères"""
    return dt.strftime(format_str)


def parse_iso_datetime(date_str: str) -> Optional[datetime]:
    """Parse une date au format ISO"""
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        log_error(f"Erreur lors du parsing de la date: {date_str}")
        return None


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Parse un JSON de manière sécurisée"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        log_error(f"Erreur lors du parsing JSON: {json_str}")
        return default


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Tronque un texte à une longueur maximale"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def create_conversation_summary(conversation: Conversation) -> str:
    """
    Crée un résumé d'une conversation pour l'affichage
    """
    if not conversation or not conversation.messages:
        return "Conversation vide"

    # Récupérer le premier message utilisateur comme titre
    first_user_msg = None
    for msg in conversation.messages:
        if msg.role == "user":
            first_user_msg = msg.content
            break

    title = truncate_text(first_user_msg or "Nouvelle conversation", 40)
    msg_count = len(conversation.messages)

    # Formatage de la date
    date_str = format_timestamp(conversation.created_at, "%d/%m/%Y")

    return f"{title} ({msg_count} messages, {date_str})"


async def run_async(func, *args, **kwargs):
    """
    Exécute une fonction synchrone de manière asynchrone
    Utile pour appeler des fonctions synchrones (comme boto3) dans un contexte asyncio
    """
    return await asyncio.to_thread(func, *args, **kwargs)


def batch_items(items: List[Any], batch_size: int = 25) -> List[List[Any]]:
    """Divise une liste d'éléments en lots"""
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


def format_response_for_telegram(text: str) -> str:
    """
    Formate le texte de réponse pour Telegram en respectant le Markdown
    Convertit le formatage Mistral AI au formatage Telegram
    """
    if not text:
        return ""
    
    import re
    
    # Convertir le formatage gras Mistral (**texte**) au formatage Telegram (*texte*)
    # Utilise une regex non-greedy pour éviter de matcher plusieurs ** sur une même ligne
    formatted_text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
    
    return formatted_text
