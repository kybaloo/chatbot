# Chatbot Telegram avec Mistral AI

[![GitHub](https://img.shields.io/badge/GitHub-kybaloo%2Fchatbot-blue?logo=github)](https://github.com/kybaloo/chatbot)

Un chatbot intelligent qui connecte Telegram à l'API Mistral AI pour offrir des conversations intelligentes aux utilisateurs. Le projet inclut une API REST avec FastAPI et est conçu pour être déployé sur AWS avec persistance des conversations via DynamoDB. Ce projet est disponible sur [GitHub](https://github.com/kybaloo/chatbot).

## 🌟 Fonctionnalités

- Bot Telegram interactif intégré à Mistral AI
- Persistance des conversations dans DynamoDB
- Historique des conversations accessibles par utilisateur
- API REST avec FastAPI pour l'intégration avec d'autres services
- Déploiement complet sur AWS (EC2 et Lambda)
- Configuration via variables d'environnement
- Logging configurable
- Conteneurisation avec Docker
- Intégration CI/CD avec Jenkins
- Gestion d'infrastructure via AWS CloudFormation

## 🛠️ Technologies utilisées

- [Python 3.12](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)
- [Mistral AI API](https://mistral.ai/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- [AWS SDK (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS DynamoDB](https://aws.amazon.com/fr/dynamodb/)
- [AWS EC2](https://aws.amazon.com/fr/ec2/)
- [Mangum](https://github.com/jordaneremieff/mangum) - Adaptateur AWS Lambda pour les applications ASGI
- [Docker](https://www.docker.com/)
- [Jenkins](https://www.jenkins.io/)

## 🚀 Installation

### Prérequis

- Python 3.12+
- Docker (optionnel)
- AWS CLI (optionnel)

### Installation locale

1. Cloner le dépôt
   ```bash
   git clone https://github.com/kybaloo/chatbot.git
   cd chatbot
   ```

2. Créer et activer un environnement virtuel

   **Option 1 : Utiliser Make**
   ```bash
   make venv
   # Sur Windows
   .venv\Scripts\activate
   # Sur Unix
   source .venv/bin/activate
   ```

   **Option 2 : Utiliser Python directement**
   ```bash
   # Sur Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # Sur Unix
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Installer les dépendances
   ```bash
   make install
   ```

4. Créer un fichier `.env` à la racine du projet avec les variables suivantes :
   ```
   ENV_NAME=local
   AWS_REGION_NAME=eu-west-3
   DYNAMO_TABLE=votre-table-dynamo
   AWS_PROFILE=votre-profil-aws
   MISTRAL_API_KEY=votre-clé-mistral
   TELEGRAM_BOT_TOKEN=votre-token-telegram
   WEBHOOK_URL=https://votre-url-webhook.com
   CONVERSATION_TTL_DAYS=30
   ```

5. Configuration du bot Telegram
   - Créez un nouveau bot en discutant avec [@BotFather](https://t.me/BotFather) sur Telegram
   - Suivez les instructions pour créer un bot et obtenir un token
   - Ajoutez le token dans votre fichier `.env` (TELEGRAM_BOT_TOKEN)

## ▶️ Exécution

### Localement avec uvicorn (développement)

```bash
# Exécuter l'API FastAPI et le bot Telegram
make run-dev

# Ou avec uvicorn directement
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Avec Docker

1. Construire l'image
   ```bash
   make build
   ```
   Ou directement avec docker :
   ```bash
   docker build -t chatbot:latest .
   ```

2. Exécuter le conteneur
   ```bash
   # Avec le Makefile
   make run-local
   
   # Ou directement avec Docker
   docker run -p 80:80 -p 8000:8000 -v $(pwd)/.env:/code/.env chatbot:latest
   ```

### Déploiement sur AWS

```bash
# Déployer l'infrastructure sur AWS
make deploy env=dev

# Configurer le webhook Telegram (uniquement pour prod/preprod)
make setup-telegram-webhook
```

## 📚 Documentation API

Une fois l'API lancée, la documentation interactive est disponible aux URLs suivantes :

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤖 Commandes du Bot Telegram

Le bot Telegram prend en charge les commandes suivantes :

- `/start` - Démarre une nouvelle conversation
- `/help` - Affiche l'aide
- `/history` - Affiche l'historique des conversations

## 🗃️ Structure du Projet

```
chatbot/
├── infrastructure/        # Infrastructure AWS CloudFormation
│   └── template.yaml      
├── src/                   # Code source du projet
│   ├── __init__.py
│   ├── config.py          # Configuration et variables d'environnement
│   ├── main.py            # Point d'entrée FastAPI
│   ├── models.py          # Modèles de données
│   ├── telegram_bot.py    # Intégration avec Telegram
│   └── utils.py           # Utilitaires et fonctions auxiliaires
├── tests/                 # Tests unitaires et d'intégration
│   ├── __init__.py
│   └── test_main.py
├── .env                   # Variables d'environnement (à créer)
├── Dockerfile             # Configuration Docker
├── Jenkinsfile            # Pipeline CI/CD
├── Makefile               # Commandes utilitaires
├── README.md              # Documentation
└── requirements.txt       # Dépendances Python
```

## 🔄 CI/CD avec Jenkins

Le projet utilise Jenkins pour l'intégration et le déploiement continus. Le pipeline est configuré pour :

1. Initialiser l'environnement
2. Exécuter les tests unitaires
3. Construire les images Docker
4. Déployer sur AWS
5. Tester les endpoints déployés

## 🛡️ Sécurité

- Les tokens et clés d'API sont stockés dans des variables d'environnement
- Les secrets Jenkins sont utilisés pour les valeurs sensibles
- L'accès à DynamoDB est limité par des politiques IAM
- Les conversations sont stockées avec chiffrement côté serveur dans DynamoDB

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez suivre les étapes suivantes :

1. Forker le dépôt
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commiter vos changements (`git commit -m 'Ajout d'une fonctionnalité incroyable'`)
4. Pousser vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚙️ Déploiement

### Sur AWS Lambda

Le projet est configuré pour être déployé sur AWS Lambda grâce à Mangum :

```bash
make infra  # Déploie l'infrastructure CloudFormation
```

### Via CI/CD

Le projet intègre un pipeline Jenkins pour l'intégration et le déploiement continus :

1. Installation et tests
2. Tests unitaires
3. (Autres étapes définies dans le Jenkinsfile)

## 🧪 Tests

```bash
pytest
```

## 📂 Structure du projet

```
├── Dockerfile            # Configuration Docker
├── Jenkinsfile           # Pipeline CI/CD Jenkins
├── LICENSE               # Fichier de licence MIT
├── Makefile              # Commandes Make
├── README.md             # Ce fichier
├── requirements.txt      # Dépendances Python
├── version               # Version du projet
└── src/                  # Code source
    ├── __init__.py
    ├── config.py         # Configuration et variables d'environnement
    ├── main.py           # Point d'entrée de l'application FastAPI
    └── utils.py          # Utilitaires (logging, etc.)
```

## 🤝 Contribution

1. Forker le projet
2. Créer une branche de fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit des changements (`git commit -am 'Ajouter une nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📝 Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT) - voir le fichier [LICENSE](LICENSE) pour plus de détails.
