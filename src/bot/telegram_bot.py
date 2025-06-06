"""
Module pour l'intégration avec Telegram
Gère l'interaction avec les utilisateurs via l'API Telegram
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime

from ..config.settings import env_vars
from ..services.conversation_service import ConversationService
from ..services.ai_service import AIService
from ..utils.logger import log_info, log_error
from ..utils.helpers import truncate_text, create_conversation_summary, format_response_for_telegram


class TelegramBot:
    """
    Classe principale pour le bot Telegram
    Gère les commandes, les callbacks et les messages
    """

    def __init__(self):
        """Initialisation du bot avec les services nécessaires"""
        self.logger = logging.getLogger(__name__)

        # Initialiser les services
        self.conversation_service = ConversationService()
        self.ai_service = AIService(model_id="mistral-small-latest")

        # Initialiser le bot Telegram
        self.bot = Bot(token=env_vars.TELEGRAM_BOT_TOKEN)
        self.application = None

        # Cache des conversations actives par utilisateur
        self.active_conversations = {}

        # Initialiser l'application
        self._initialize_application()

        log_info("TelegramBot initialized")

    async def set_bot_commands(self):
        """Définir les commandes du bot qui seront affichées dans l'interface de Telegram"""
        commands = [
            ("start", "Démarrer une nouvelle conversation"),
            ("help", "Afficher l'aide"),
            ("history", "Afficher l'historique des conversations"),
            ("new", "Créer une nouvelle conversation"),
            ("settings", "Modifier les paramètres")
        ]
        
        try:
            await self.bot.set_my_commands(commands)
            log_info("Commandes du bot définies avec succès")
        except Exception as e:
            log_error(f"Erreur lors de la définition des commandes du bot: {str(e)}")

    def _initialize_application(self):
        """Initialise l'application Telegram"""
        self.application = (
            Application.builder().token(env_vars.TELEGRAM_BOT_TOKEN).build()
        )

        # Ajouter les gestionnaires de commandes
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("new", self.new_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))

        # Gestionnaires pour les interactions avancées
        self.application.add_handler(
            CallbackQueryHandler(self.handle_conversation_selection, pattern=r"^conv_")
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handle_model_selection, pattern=r"^model_")
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handle_settings_selection, pattern=r"^settings_")
        )

        # Gestionnaire pour les messages texte
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        # Gestionnaire d'erreurs
        self.application.add_error_handler(self.error_handler)

    async def process_update(self, update_data: dict):
        """
        Traite une mise à jour reçue via webhook

        Args:
            update_data: Données JSON de la mise à jour Telegram
        """
        try:
            # Créer un objet Update à partir des données JSON
            update = Update.de_json(update_data, self.bot)

            # Traiter la mise à jour avec l'application
            await self.application.process_update(update)

        except Exception as e:
            log_error(f"Erreur lors du traitement de la mise à jour: {str(e)}")
            raise

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gère la commande /start
        Crée une nouvelle conversation et envoie un message d'accueil
        """
        user = update.effective_user
        log_info(f"User {user.id} ({user.username}) started the bot")

        # Créer une nouvelle conversation
        conversation = await self.conversation_service.create_new_conversation(
            user_id=str(user.id), username=user.username
        )

        # Mettre en cache la conversation active
        self.active_conversations[user.id] = conversation.conversation_id

        # Créer un clavier inline avec des boutons d'action rapide
        keyboard = [
            [
                InlineKeyboardButton("Nouvelle conversation", callback_data="conv_new"),
                InlineKeyboardButton("Historique", callback_data="conv_history"),
            ],
            [
                InlineKeyboardButton("Aide", callback_data="settings_help"),
                InlineKeyboardButton("Paramètres", callback_data="settings_main"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Bonjour {user.first_name} ! 👋\n\n"
            f"Je suis votre assistant IA personnel, propulsé par Mistral AI. "
            f"Je peux vous aider à répondre à vos questions, discuter de divers sujets "
            f"et bien plus encore.\n\n"
            f"Comment puis-je vous aider aujourd'hui ?",
            reply_markup=reply_markup,
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gère la commande /help
        Affiche l'aide et les commandes disponibles
        """
        help_text = (
            "🤖 *Commandes disponibles* 🤖\n\n"
            "• /start - Démarre une nouvelle conversation\n"
            "• /new - Crée une nouvelle conversation\n"
            "• /history - Affiche l'historique de vos conversations\n"
            "• /settings - Personnalisez vos préférences\n"
            "• /help - Affiche cette aide\n\n"
            "💬 *Utilisation* 💬\n"
            "Envoyez-moi simplement un message et je vous répondrai. "
            "Toutes vos conversations sont sauvegardées et vous pouvez "
            "y revenir à tout moment via la commande /history.\n\n"
            "⚙️ *Fonctionnalités* ⚙️\n"
            "• Conservation du contexte des conversations\n"
            "• Historique complet accessible\n"
            "• Possibilité de basculer entre différents modèles d'IA\n"
            "• Interface intuitive avec boutons\n\n"
            "Pour toute question ou problème, n'hésitez pas à contacter l'administrateur."
        )

        # Créer un clavier inline avec des boutons d'action rapide
        keyboard = [
            [
                InlineKeyboardButton("Nouvelle conversation", callback_data="conv_new"),
                InlineKeyboardButton("Historique", callback_data="conv_history"),
            ],
            [InlineKeyboardButton("Paramètres", callback_data="settings_main")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            help_text, reply_markup=reply_markup, parse_mode="MarkdownV2"
        )

    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gère la commande /history
        Affiche l'historique des conversations de l'utilisateur
        """
        user = update.effective_user
        user_id = str(user.id)

        # Récupérer les conversations de l'utilisateur
        conversations = await self.conversation_service.get_by_user(user_id)

        if not conversations:
            await update.message.reply_text(
                "Vous n'avez pas encore d'historique de conversations. "
                "Commencez à discuter avec moi pour en créer une !"
            )
            return

        # Trier les conversations par date de mise à jour (la plus récente d'abord)
        conversations.sort(key=lambda c: c.updated_at, reverse=True)

        # Créer un clavier inline avec les conversations
        keyboard = []
        for conv in conversations[
            :10
        ]:  # Limiter à 10 conversations pour éviter un clavier trop grand
            # Créer un résumé de la conversation
            summary = create_conversation_summary(conv)
            keyboard.append(
                [
                    InlineKeyboardButton(
                        summary, callback_data=f"conv_{conv.conversation_id}"
                    )
                ]
            )

        # Ajouter un bouton pour créer une nouvelle conversation
        keyboard.append(
            [InlineKeyboardButton("➕ Nouvelle conversation", callback_data="conv_new")]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📚 *Voici vos conversations récentes* 📚\n"
            "Sélectionnez une conversation pour la continuer :",
            reply_markup=reply_markup,
            parse_mode="MarkdownV2",
        )

    async def new_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gère la commande /new
        Crée une nouvelle conversation
        """
        user = update.effective_user
        user_id = str(user.id)

        # Créer une nouvelle conversation
        conversation = await self.conversation_service.create_new_conversation(
            user_id=user_id, username=user.username
        )

        # Mettre à jour la conversation active
        self.active_conversations[user.id] = conversation.conversation_id

        await update.message.reply_text(
            "✨ J'ai créé une nouvelle conversation pour vous. Comment puis-je vous aider ?"
        )

    async def settings_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Gère la commande /settings
        Affiche et permet de modifier les paramètres de l'utilisateur
        """
        # Créer un clavier inline avec les options de paramètres
        keyboard = [
            [
                InlineKeyboardButton(
                    "🤖 Changer de modèle d'IA", callback_data="settings_model"
                )
            ],
            [
                InlineKeyboardButton(
                    "🌍 Changer de langue", callback_data="settings_language"
                )
            ],
            [
                InlineKeyboardButton(
                    "📝 Style de réponse", callback_data="settings_style"
                )
            ],
            [InlineKeyboardButton("⬅️ Retour", callback_data="settings_back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "⚙️ *Paramètres* ⚙️\n\n"
            "Personnalisez votre expérience en modifiant les paramètres ci-dessous :",
            reply_markup=reply_markup,
            parse_mode="MarkdownV2",
        )

    async def handle_conversation_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Gère la sélection d'une conversation depuis le menu d'historique
        """
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        user_id = str(user.id)
        data = query.data

        # Vérifier s'il s'agit d'une nouvelle conversation
        if data == "conv_new":
            # Créer une nouvelle conversation
            conversation = await self.conversation_service.create_new_conversation(
                user_id=user_id, username=user.username
            )

            # Mettre à jour la conversation active
            self.active_conversations[user.id] = conversation.conversation_id

            await query.edit_message_text(
                "✨ J'ai créé une nouvelle conversation pour vous. Comment puis-je vous aider ?"
            )
            return

        # Récupérer l'ID de la conversation à partir du callback data
        # Format: "conv_<conversation_id>"
        conversation_id = data.split("_")[1]

        # Récupérer la conversation
        conversation = await self.conversation_service.get_by_user_and_conversation(
            user_id, conversation_id
        )

        if not conversation:
            await query.edit_message_text(
                "⚠️ Désolé, cette conversation n'existe plus ou n'est pas accessible."
            )
            return

        # Mettre à jour la conversation active
        self.active_conversations[user.id] = conversation_id

        # Préparer un aperçu des messages
        messages_preview = ""
        max_preview_messages = 5

        # Récupérer les derniers messages (limités)
        preview_messages = (
            conversation.messages[-max_preview_messages:]
            if len(conversation.messages) > max_preview_messages
            else conversation.messages
        )

        # Ajouter une indication si certains messages ne sont pas affichés
        if len(conversation.messages) > max_preview_messages:
            remaining = len(conversation.messages) - max_preview_messages
            messages_preview += f"... et {remaining} autres messages antérieurs\n\n"

        # Formater l'aperçu des messages
        for message in preview_messages:
            role_display = "Vous" if message.role == "user" else "Assistant"
            content_preview = truncate_text(message.content, 100)
            messages_preview += f"*{role_display}*: {content_preview}\n\n"

        # Créer un clavier inline
        keyboard = [
            [
                InlineKeyboardButton(
                    "📝 Renommer", callback_data=f"settings_rename_{conversation_id}"
                ),
                InlineKeyboardButton(
                    "🗑️ Supprimer", callback_data=f"settings_delete_{conversation_id}"
                ),
            ],
            [InlineKeyboardButton("📚 Historique", callback_data="conv_history")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"*Conversation du {conversation.created_at.strftime('%d/%m/%Y')}*\n\n"
            f"{messages_preview}\n"
            f"La conversation est maintenant active. Vous pouvez continuer à échanger des messages.",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2',
        )

    async def handle_model_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Gère la sélection d'un modèle d'IA depuis les paramètres
        """
        query = update.callback_query
        await query.answer()

        data = query.data

        # Récupérer l'ID du modèle à partir du callback data
        # Format: "model_<model_id>"
        if data == "model_list":
            # Afficher la liste des modèles disponibles
            models = self.ai_service.get_available_models()

            # Créer un clavier inline avec les modèles disponibles
            keyboard = []
            for model in models:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"{model['name']} - {model['description'][:30]}...",
                            callback_data=f"model_{model['model_id']}",
                        )
                    ]
                )

            keyboard.append(
                [InlineKeyboardButton("⬅️ Retour", callback_data="settings_main")]
            )
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "🤖 *Sélectionnez un modèle d'IA* 🤖\n\n"
                "Choisissez le modèle que vous souhaitez utiliser pour vos conversations :",
                reply_markup=reply_markup,
                parse_mode='MarkdownV2',
            )
            return

        # Changer le modèle d'IA
        model_id = data.split("_")[1]
        success = self.ai_service.switch_model(model_id)

        if not success:
            await query.edit_message_text(
                "⚠️ Désolé, ce modèle n'est pas disponible actuellement."
            )
            return

        # Afficher un message de confirmation
        await query.edit_message_text(
            f"✅ Le modèle a été changé avec succès pour {self.ai_service.model_id}."
        )

    async def handle_settings_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Gère la sélection d'options dans le menu des paramètres
        """
        query = update.callback_query
        await query.answer()

        data = query.data

        # Gérer les différentes options de paramètres
        if data == "settings_model":
            # Rediriger vers la sélection de modèle
            await self.handle_model_selection(update, context)
        elif data == "settings_language":
            # TODO: Implémenter la sélection de langue
            await query.edit_message_text(
                "🚧 La sélection de langue sera disponible prochainement. 🚧"
            )
        elif data == "settings_style":
            # TODO: Implémenter la sélection de style
            await query.edit_message_text(
                "🚧 La personnalisation du style de réponse sera disponible prochainement. 🚧"
            )
        elif data == "settings_back" or data == "settings_main":
            # Retour au menu principal des paramètres
            await self.settings_command(update, context)
        elif data.startswith("settings_delete_"):
            # Supprimer une conversation
            conversation_id = data.split("_")[2]
            user_id = str(update.effective_user.id)

            success = await self.conversation_service.delete_by_user_and_conversation(
                user_id, conversation_id
            )

            if success:
                await query.edit_message_text(
                    "✅ La conversation a été supprimée avec succès."
                )
            else:
                await query.edit_message_text(
                    "⚠️ Impossible de supprimer cette conversation."
                )
        elif data.startswith("settings_rename_"):
            # TODO: Implémenter le renommage de conversation
            await query.edit_message_text(
                "🚧 Le renommage de conversation sera disponible prochainement. 🚧"
            )
        elif data == "settings_help":
            # Afficher l'aide
            await self.help_command(update, context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gère les messages texte reçus de l'utilisateur
        """
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text

        # Récupérer ou créer une conversation
        conversation_id = self.active_conversations.get(user.id)
        conversation = None

        if conversation_id:
            conversation = await self.conversation_service.get_by_user_and_conversation(
                user_id, conversation_id
            )

        if not conversation:
            # Créer une nouvelle conversation si aucune n'est active
            conversation = await self.conversation_service.create_new_conversation(
                user_id, user.username
            )
            self.active_conversations[user.id] = conversation.conversation_id

        # Ajouter le message utilisateur à la conversation
        conversation.add_message(role="user", content=message_text)

        # Envoyer un message "en train d'écrire"
        await update.message.chat.send_action(action="typing")

        try:
            # Traiter la conversation avec le service IA
            assistant_response = await self.ai_service.process_conversation(
                conversation
            )

            if not assistant_response:
                raise Exception("Pas de réponse du modèle d'IA")

            # Ajouter la réponse à la conversation
            conversation.add_message(role="assistant", content=assistant_response)

            # Sauvegarder la conversation mise à jour
            await self.conversation_service.update(
                conversation.conversation_id, conversation
            )

            # Formater la réponse pour Telegram et l'envoyer à l'utilisateur
            formatted_response = format_response_for_telegram(assistant_response)
            await update.message.reply_text(formatted_response, parse_mode="MarkdownV2")

        except Exception as e:
            log_error(f"Erreur lors du traitement du message: {str(e)}")
            await update.message.reply_text(
                "Désolé, j'ai rencontré un problème lors du traitement de votre message. "
                "Veuillez réessayer plus tard."
            )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gère les erreurs rencontrées par le dispatcher
        """
        error_message = f"Exception lors du traitement d'une mise à jour: {context.error}"
        log_error(error_message)
        
        # Journaliser plus de détails pour le débogage
        if hasattr(context.error, "__traceback__"):
            import traceback
            tb_str = ''.join(traceback.format_tb(context.error.__traceback__))
            log_error(f"Traceback: {tb_str}")

        # Informer l'utilisateur d'une erreur
        if update and update.effective_message:
            # En mode développement, on peut envoyer l'erreur complète au client
            if env_vars.ENV_NAME == "local" or env_vars.ENV_NAME == "dev":
                await update.effective_message.reply_text(
                    f"Erreur de développement: {context.error}\n\nVeuillez vérifier les logs pour plus de détails."
                )
            else:
                await update.effective_message.reply_text(
                    "Désolé, une erreur s'est produite lors du traitement de votre message."
                )

    def run(self):
        """
        Lance le bot Telegram en mode webhook
        """
        log_info("Bot Telegram initialisé pour mode webhook")
        # En mode webhook, nous n'utilisons pas run_webhook() ici
        # car le traitement se fait via process_update() appelé par FastAPI

    async def initialize(self):
        """
        Initialise l'application Telegram de manière asynchrone
        Cette méthode doit être appelée avant d'utiliser le bot
        """
        try:
            if self.application:
                # Initialiser le bot lui-même avant d'initialiser l'application
                await self.bot.initialize()
                
                # Initialiser l'application
                await self.application.initialize()
                
                # Définir les commandes du bot pour qu'elles apparaissent dans l'interface Telegram
                await self.set_bot_commands()
                
                log_info("Application Telegram initialisée avec succès")
            else:
                raise Exception("Application Telegram non créée")
        except Exception as e:
            log_error(f"Erreur lors de l'initialisation de l'application Telegram: {str(e)}")
            raise

    async def shutdown(self):
        """
        Arrête proprement l'application Telegram
        """
        try:
            if self.application:
                await self.application.shutdown()
                log_info("Application Telegram arrêtée proprement")
        except Exception as e:
            log_error(f"Erreur lors de l'arrêt de l'application Telegram: {str(e)}")
