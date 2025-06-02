# Guide de Démarrage Rapide - ChatBot Telegram

Ce guide vous aidera à configurer et démarrer rapidement votre ChatBot Telegram intégré avec Mistral AI.

## 🚀 Étapes de Configuration

### 1. Vérification de la Configuration

Avant de commencer, vérifiez que votre configuration est correcte :

```powershell
python scripts/test_config.py
```

Ce script vérifie :
- Les variables d'environnement
- Les modules Python installés
- Le format de l'URL webhook
- L'instanciation du bot

### 2. Démarrage du Serveur

Démarrez votre serveur FastAPI :

```powershell
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Le serveur sera accessible sur `http://localhost:8000`

### 3. Configuration du Tunnel (Développement Local)

Si vous développez en local, utilisez ngrok pour exposer votre serveur :

```powershell
# Dans un nouveau terminal
ngrok http 8000
```

Copiez l'URL HTTPS générée et mettez à jour votre fichier `.env` :

```env
WEBHOOK_URL="https://your-ngrok-url.ngrok-free.app/webhook/telegram"
```

### 4. Configuration du Webhook Telegram

Configurez le webhook Telegram avec votre URL :

```powershell
python scripts/setup_ngrok_webhook.py
```

Ce script :
- Teste l'accessibilité de votre endpoint
- Configure le webhook Telegram
- Vérifie la configuration

### 5. Test du Bot

Envoyez un message à votre bot sur Telegram pour tester :

1. Cherchez votre bot sur Telegram (`@votre_bot_name`)
2. Envoyez `/start` pour commencer
3. Envoyez un message pour tester l'intégration avec Mistral AI

## 📁 Structure des Endpoints

### API REST
- `GET /` - Page d'accueil
- `GET /chat` - Endpoint de chat direct
- `GET /conversations/{user_id}` - Lister les conversations d'un utilisateur
- `GET /conversations/{user_id}/{conversation_id}` - Récupérer une conversation

### Webhook Telegram
- `POST /webhook/telegram` - Endpoint pour recevoir les mises à jour Telegram

## 🔧 Dépannage

### Erreur 404 sur le Webhook

Si Telegram retourne une erreur 404 :

1. Vérifiez que votre serveur FastAPI est en cours d'exécution
2. Vérifiez que l'URL dans `.env` se termine par `/webhook/telegram`
3. Testez l'endpoint manuellement :
   ```powershell
   curl -X POST https://your-url.ngrok-free.app/webhook/telegram
   ```

### Erreurs d'Import

Si vous avez des erreurs d'import de modules :

```powershell
pip install -r requirements.txt
```

### Problèmes de Connexion DynamoDB

Pour le développement local avec DynamoDB :

```powershell
# Démarrer DynamoDB local
./scripts/setup_local_dynamo.ps1

# Créer la table de test
python scripts/create_local_table.py
```

## 🎯 Commandes du Bot Telegram

- `/start` - Démarre une nouvelle conversation
- `/help` - Affiche l'aide
- `/history` - Affiche l'historique des conversations

## 📊 Monitoring

### Logs du Serveur
Les logs du serveur FastAPI s'affichent dans le terminal où vous avez lancé `uvicorn`.

### Informations du Webhook
Utilisez le script de diagnostic pour vérifier l'état du webhook :

```powershell
python scripts/diagnose_webhook.py
```

### Logs des Conversations
Les conversations sont automatiquement sauvegardées dans DynamoDB avec un TTL configurable.

## 🚢 Déploiement en Production

Pour déployer en production sur AWS :

1. Consultez le guide de déploiement AWS : `AWS_DEPLOYMENT_GUIDE.md`
2. Utilisez le template CloudFormation : `infrastructure/template.yaml`
3. Configurez le pipeline Jenkins : `Jenkinsfile`

## 🔒 Sécurité

### Variables d'Environnement Sensibles
- `TELEGRAM_BOT_TOKEN` - Token de votre bot Telegram
- `MISTRAL_API_KEY` - Clé API Mistral AI
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` - Identifiants AWS

### Recommandations
- Ne commitez jamais le fichier `.env` dans Git
- Utilisez AWS Secrets Manager en production
- Limitez les permissions DynamoDB au minimum nécessaire
- Activez HTTPS uniquement pour le webhook

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs du serveur FastAPI
2. Utilisez `python scripts/test_config.py` pour diagnostiquer
3. Consultez la documentation des APIs utilisées :
   - [python-telegram-bot](https://docs.python-telegram-bot.org/)
   - [Mistral AI](https://docs.mistral.ai/)
   - [FastAPI](https://fastapi.tiangolo.com/)
