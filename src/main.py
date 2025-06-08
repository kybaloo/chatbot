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
    log_info(f"Démarrage de l'application dans l'environnement: {env_vars.ENV_NAME}...")
    
    # Initialiser le bot Telegram si configuré
    telegram_bot_instance = None
    if env_vars.TELEGRAM_BOT_TOKEN:
        try:
            from .bot.telegram_bot import TelegramBot
            import asyncio

            log_info("Initialisation du bot Telegram pour le mode webhook")
            
            # Créer l'instance du bot Telegram
            telegram_bot_instance = TelegramBot()
            
            # Initialiser le bot avec un mécanisme de retry pour plus de robustesse
            max_retries = 3
            retry_delay = 1  # secondes
            
            for attempt in range(max_retries):
                try:
                    # Initialiser explicitement le bot Telegram
                    await telegram_bot_instance.initialize()
                    log_info("Bot Telegram initialisé avec succès")
                    break
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        log_error(f"Tentative {attempt+1}/{max_retries} échouée: {str(retry_error)}. Nouvel essai dans {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Backoff exponentiel
                    else:
                        raise
            
            # Ajouter le bot à l'état de l'application pour y accéder ailleurs
            app.state.telegram_bot = telegram_bot_instance
        except Exception as e:
            log_error(f"Erreur lors de l'initialisation du bot Telegram: {str(e)}")
            # Continuer sans le bot Telegram si l'initialisation échoue
            app.state.telegram_bot = None
    else:
        log_info("Bot Telegram non configuré (TELEGRAM_BOT_TOKEN manquant)")
        app.state.telegram_bot = None
    
    yield
    
    log_info("Arrêt de l'application...")
    
    # Arrêter proprement le bot Telegram si initialisé
    if hasattr(app.state, "telegram_bot") and app.state.telegram_bot:
        try:
            await app.state.telegram_bot.shutdown()
            log_info("Bot Telegram arrêté proprement")
        except Exception as e:
            log_error(f"Erreur lors de l'arrêt du bot Telegram: {str(e)}")
            # Continuer même si l'arrêt du bot échoue


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
    import asyncio
    
    if not hasattr(app.state, "telegram_bot") or not app.state.telegram_bot:
        log_error("Bot Telegram non initialisé")
        raise HTTPException(status_code=500, detail="Bot Telegram non initialisé")

    try:
        # Vérifier que la requête contient du JSON valide
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            log_error(f"Content-Type invalide: {content_type}")
            raise HTTPException(status_code=400, detail="Content-Type doit être application/json")

        # Récupérer les données JSON de la requête
        try:
            update_data = await request.json()
        except Exception as json_error:
            log_error(f"Erreur de parsing JSON: {str(json_error)}")
            raise HTTPException(status_code=400, detail="JSON invalide")

        if not update_data:
            log_error("Données de mise à jour vides")
            raise HTTPException(status_code=400, detail="Données vides")

        # Limiter les logs pour éviter de surcharger CloudWatch
        # Log uniquement des informations minimales sur la mise à jour
        if "update_id" in update_data:
            log_info(f"Mise à jour Telegram reçue: ID={update_data.get('update_id')}")
        else:
            log_info(f"Mise à jour Telegram reçue sans update_id")

        # Traiter la mise à jour avec le bot Telegram - en mode non bloquant
        # Ne pas attendre que la mise à jour soit entièrement traitée
        # Cela permet de renvoyer rapidement une réponse au webhook de Telegram
        asyncio.create_task(app.state.telegram_bot.process_update(update_data))
        
        # Répondre immédiatement au webhook
        return {"status": "ok"}

    except HTTPException:
        # Re-lever les HTTPException sans les modifier
        raise
    except Exception as e:
        log_error(f"Erreur lors du traitement du webhook Telegram: {str(e)}")
        # Même en cas d'erreur, répondre avec un statut 200 pour éviter que Telegram ne réessaie
        # Les erreurs sont loggées et peuvent être analysées dans CloudWatch
        return {"status": "error", "message": str(e)}


# Handler pour AWS Lambda via Mangum
handler = Mangum(app)


# Point d'entrée pour l'exécution directe (développement local)
if __name__ == "__main__":
    import uvicorn

    log_info("Démarrage du serveur de développement...")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)