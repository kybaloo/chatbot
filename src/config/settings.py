"""
Configuration de l'application via variables d'environnement
Utilise pydantic-settings pour la validation et le chargement
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os
from typing import Optional


class Settings(BaseSettings):
    """Classe de configuration principale de l'application"""
    
    # Configuration de l'environnement
    ENV_NAME: str = "local"
    
    # Configuration AWS
    AWS_REGION_NAME: str = ""
    DYNAMO_TABLE: str = ""
    
    # Configuration API
    MISTRAL_API_KEY: str = ""
    
    # Configuration Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    WEBHOOK_URL: str = ""  # URL pour le webhook Telegram
    
    # Configuration de l'application
    CONVERSATION_TTL_DAYS: int = 30  # Durée de rétention des conversations en jours
    LOG_LEVEL: str = "INFO"
    
    # Configuration de la base de données
    USE_LOCAL_DB: bool = False  # Si True, utilise une DB locale pour le développement
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Retourne une instance singleton des paramètres de l'application
    Utilise lru_cache pour éviter de relire le fichier .env à chaque appel
    """
    return Settings()


# Instance globale des paramètres, à utiliser dans toute l'application
env_vars = get_settings()
