"""
Configuration et utilitaires de logging
"""

import logging
import sys
from ..config.settings import env_vars


def setup_logger():
    """Configure le système de logging pour l'application"""
    # Déterminer le niveau de log à partir de la configuration
    log_level_str = env_vars.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Configuration de base
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("app.log")],
    )

    # Réduire la verbosité des logs de certaines bibliothèques
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger("chatbot")
    logger.info(f"Logging configured with level {log_level_str}")

    return logger


# Logger global pour l'application
app_logger = setup_logger()


def get_logger(name: str = None):
    """Récupère un logger configuré pour un module spécifique"""
    if name:
        return logging.getLogger(f"chatbot.{name}")
    return app_logger


# Fonctions utilitaires pour les logs
def log_info(message: str):
    """Log un message de niveau INFO"""
    app_logger.info(message)


def log_error(message: str, exc_info=False):
    """Log un message de niveau ERROR"""
    app_logger.error(message, exc_info=exc_info)


def log_warning(message: str):
    """Log un message de niveau WARNING"""
    app_logger.warning(message)


def log_debug(message: str):
    """Log un message de niveau DEBUG"""
    app_logger.debug(message)
