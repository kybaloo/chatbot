"""
Point d'entrée principal de l'application
Intègre tous les modules de l'application (API, bot Telegram, services)
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from mangum import Mangum
import logging
import sys

from .config.settings import env_vars
from .api.routes import router as api_router
from .utils.logger import setup_logger, log_info, log_error

# Initialiser le logger
logger = setup_logger()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application
    Initialise les ressources au démarrage et les nettoie à l'arrêt
    """
    log_info("Démarrage de l'application...")
    
    # Initialiser le bot Telegram si configuré
    telegram_bot_instance = None
    if env_vars.TELEGRAM_BOT_TOKEN:
        try:
            from .bot.telegram_bot import TelegramBot
            log_info("Initialisation du bot Telegram pour le mode webhook")
            telegram_bot_instance = TelegramBot()
            # Ajouter le bot à l'état de l'application pour y accéder ailleurs
            app.state.telegram_bot = telegram_bot_instance
        except Exception as e:
            log_error(f"Erreur lors de l'initialisation du bot Telegram: {str(e)}")
    else:
        log_info("Bot Telegram non configuré (TELEGRAM_BOT_TOKEN manquant)")
    
    yield
    
    log_info("Arrêt de l'application...")


# Création de l'application FastAPI
app = FastAPI(
    title="ChatBot API",
    description="API pour un chatbot intelligent basé sur Mistral AI et Telegram",
    version="1.0.0",
    lifespan=app_lifespan,
)

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajout des routes de l'API
app.include_router(api_router)


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """
    Endpoint webhook pour recevoir les mises à jour de Telegram
    """
    if not hasattr(app.state, "telegram_bot") or not app.state.telegram_bot:
        raise HTTPException(status_code=500, detail="Bot Telegram non initialisé")
    
    try:
        # Récupérer les données JSON de la requête
        update_data = await request.json()
        log_info(f"Mise à jour Telegram reçue: {update_data}")
        
        # Traiter la mise à jour avec le bot Telegram
        await app.state.telegram_bot.process_update(update_data)
        
        return {"status": "ok"}
    
    except Exception as e:
        log_error(f"Erreur lors du traitement du webhook Telegram: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


# Handler pour AWS Lambda via Mangum
handler = Mangum(app)


# Point d'entrée pour l'exécution directe (développement local)
if __name__ == "__main__":
    import uvicorn
    log_info("Démarrage du serveur de développement...")
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
