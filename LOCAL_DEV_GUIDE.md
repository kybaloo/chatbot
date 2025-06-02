# Guide de développement local pour le ChatBot Telegram

Ce document explique comment configurer et exécuter le projet en mode développement local.

## Prérequis

- Python 3.12+
- Java Runtime Environment (pour DynamoDB Local)
- ngrok (pour le webhook Telegram)
- Un compte Telegram et un token de bot (via BotFather)
- Une clé API Mistral AI

## Installation des outils

### Ngrok
1. Téléchargez ngrok depuis [https://ngrok.com/download](https://ngrok.com/download)
2. Extrayez le fichier téléchargé
3. Ajoutez ngrok à votre PATH système ou placez-le dans un dossier accessible

### Java
Assurez-vous que Java est installé sur votre système. Vous pouvez vérifier en exécutant :
```
java -version
```

## Configuration du projet

1. **Cloner le dépôt**
   ```
   git clone <URL_DU_REPOS>
   cd chatbot
   ```

2. **Créer et activer l'environnement virtuel**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```
   pip install -r requirements.txt
   ```

4. **Configurer le fichier .env**
   - Copiez le fichier `.env.example` vers `.env`
   - Remplissez les valeurs requises, notamment :
     - `MISTRAL_API_KEY` : Votre clé API Mistral
     - `TELEGRAM_BOT_TOKEN` : Le token de votre bot Telegram

## Démarrage des services

### Option 1 : Script d'installation automatique

Exécutez le script d'installation qui vous guidera à travers le processus :
```powershell
.\dev_setup.ps1
```

### Option 2 : Étapes manuelles

1. **Démarrer DynamoDB Local**
   ```powershell
   .\setup_local_dynamo.ps1
   ```

2. **Créer la table DynamoDB locale**
   ```
   python scripts\create_local_table.py
   ```

3. **Configurer le webhook Telegram avec ngrok**
   ```
   python scripts\setup_ngrok_webhook.py
   ```

4. **Démarrer l'application FastAPI**
   ```
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Option 3 : Utiliser Make (recommandé pour les utilisateurs Linux/Mac)

```
make run-local-dynamo  # Dans un terminal séparé
make create-local-table
make setup-ngrok       # Dans un terminal séparé
make run-dev
```

## Tester le bot

1. Ouvrez Telegram et cherchez votre bot par son nom d'utilisateur
2. Commencez une conversation avec la commande `/start`
3. Le bot devrait répondre et vous pouvez commencer à lui envoyer des messages

## Structure des fichiers de développement

- `dev_setup.ps1` : Script principal pour la configuration de l'environnement de développement
- `setup_local_dynamo.ps1` : Script pour démarrer DynamoDB Local
- `scripts/create_local_table.py` : Script pour créer la table DynamoDB locale
- `scripts/setup_ngrok_webhook.py` : Script pour configurer le webhook Telegram avec ngrok

## Dépannage

### Problèmes avec DynamoDB Local
- Vérifiez que Java est correctement installé
- Vérifiez que le port 8000 est disponible
- Si DynamoDB Local ne démarre pas, essayez de télécharger manuellement le JAR depuis [le site AWS](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html)

### Problèmes avec ngrok
- Vérifiez que ngrok est correctement installé et accessible
- Si le webhook ne se configure pas, vérifiez votre token Telegram
- Assurez-vous que votre application FastAPI fonctionne sur le port 8000

### Problèmes avec le bot Telegram
- Vérifiez que votre token bot est valide
- Assurez-vous que le webhook est correctement configuré
- Vérifiez les journaux de l'application pour détecter les erreurs

## Ressources utiles

- [Documentation Telegram Bot API](https://core.telegram.org/bots/api)
- [Documentation AWS DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)
- [Documentation Mistral AI](https://docs.mistral.ai/)
- [Documentation ngrok](https://ngrok.com/docs)