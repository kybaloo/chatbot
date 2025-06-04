# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### À venir
- Interface web d'administration
- Tests de performance automatisés
- Analyse de sécurité intégrée
- Notifications pipeline (Slack/Teams)

## [1.0.2] - 2025-06-04

### 🚀 Amélioré
#### Pipeline Jenkins optimisé
- **Nouvelle étape** : Vérification de version au début du pipeline
- **Code Quality amélioré** : Ajout du linting avec flake8 après formatage
- **Documentation automatique** : Génération Sphinx intégrée au pipeline
- **Traçabilité** : Version visible dans chaque build Jenkins

#### Nouvelle documentation
- `PIPELINE_IMPROVEMENTS.md` : Analyse comparative détaillée Makefile vs Jenkinsfile
- Documentation des 11 étapes du pipeline optimisé vs 8 étapes originales
- Guide des commandes Make disponibles pour développement et production

### 🔧 Technique
- Pipeline Jenkins : +3 étapes pour améliorer la qualité et traçabilité
- Détection précoce des problèmes de code avec linting automatique
- Documentation Sphinx mise à jour automatiquement à chaque build
- Couverture qualité complète : Formatage + Linting + Tests + Documentation
- Support multimodal (images, audio)
- Système de plugins extensible
- Intégration avec d'autres plateformes de messagerie

## [1.0.1] - 2025-06-04

### Ajouté
- 📚 **Documentation complète** pour les contributeurs
  - Guide de contribution détaillé ([CONTRIBUTING.md](CONTRIBUTING.md))
  - Politique de sécurité ([SECURITY.md](SECURITY.md))
  - Liste des contributeurs ([CONTRIBUTORS.md](CONTRIBUTORS.md))
  - Guide de démarrage ultra-rapide ([QUICK_SETUP.md](QUICK_SETUP.md))
- 🔧 **Templates GitHub** pour améliorer la collaboration
  - Template pour signaler des bugs (.github/ISSUE_TEMPLATE/bug_report.md)
  - Template pour proposer des fonctionnalités (.github/ISSUE_TEMPLATE/feature_request.md)
  - Template pour les Pull Requests (.github/pull_request_template.md)
- 🛡️ **Documentation de sécurité** avec bonnes pratiques et processus de signalement
- 🏆 **Système de reconnaissance** des contributeurs avec hall of fame
- 📋 **Standards de qualité** détaillés pour le développement

### Amélioré
- 📖 **README.md** enrichi avec liens vers la nouvelle documentation
- 🔄 **Processus de contribution** standardisé avec guidelines claires
- 🧪 **Guide de tests** avec exemples et métriques de qualité
- ⚡ **Setup express** pour démarrage en moins de 5 minutes

### Documenté
- 🎯 **Architecture en couches** avec diagrammes détaillés
- 📊 **Métriques de qualité** (couverture, complexité, conformité)
- 🔐 **Bonnes pratiques de sécurité** pour tous les environnements
- 🚀 **Workflows de développement** avec exemples pratiques

## [1.0.0] - 2025-06-04

### Ajouté
- 🚀 **Architecture complètement refactorisée** avec séparation des couches
- 📊 **Modèles de données enrichis** (User, Conversation, Message, AIModel)
- 🗄️ **Pattern Repository** pour l'accès aux données DynamoDB
- 🔧 **Couche Service** pour la logique métier
- ⚙️ **Configuration centralisée** avec pydantic-settings
- 🤖 **Bot Telegram avancé** avec commandes enrichies
- 📚 **API REST complète** avec FastAPI
- 🔐 **Gestion des utilisateurs** et préférences
- 💬 **Historique des conversations** persistant
- 🎯 **Support multi-modèles Mistral AI** avec paramètres configurables
- 📱 **Interface utilisateur améliorée** avec boutons inline
- 🔄 **Webhook Telegram** pour une meilleure réactivité
- 🚀 **Déploiement AWS** avec Lambda + API Gateway + DynamoDB
- 🐳 **Conteneurisation Docker** complète
- 🔧 **Pipeline CI/CD Jenkins** automatisé
- 📋 **Tests unitaires et d'intégration** complets
- 📖 **Documentation technique** détaillée

### Fonctionnalités principales
- Chat intelligent avec Mistral AI
- Persistance des conversations dans DynamoDB
- Gestion multi-utilisateurs
- Configuration flexible des modèles IA
- Interface de commandes Telegram intuitive
- API REST pour intégrations tierces
- Monitoring et logging avancés
- Déploiement cloud-native sur AWS

### Commandes Bot Telegram
- `/start` - Démarrer une conversation
- `/help` - Afficher l'aide
- `/history` - Consulter l'historique des conversations
- `/settings` - Configurer les préférences
- `/new` - Créer une nouvelle conversation
- `/models` - Changer de modèle IA

### API Endpoints
- `GET /` - Endpoint de santé
- `POST /chat` - Chat avec l'IA
- `GET /conversations/{user_id}` - Récupérer les conversations
- `POST /webhook/telegram` - Webhook Telegram
- `GET /docs` - Documentation interactive (Swagger)

### Technologies utilisées
- **Backend**: Python 3.12, FastAPI, Pydantic
- **IA**: Mistral AI API (mistral-large, mistral-medium, mistral-small)
- **Bot**: python-telegram-bot 22.x
- **Base de données**: AWS DynamoDB
- **Cloud**: AWS Lambda, API Gateway, EC2
- **Containerisation**: Docker
- **CI/CD**: Jenkins
- **Infrastructure**: AWS CloudFormation (SAM)
- **Monitoring**: CloudWatch, logging structuré

### Sécurité
- Variables d'environnement pour les secrets
- Validation des entrées avec Pydantic
- Gestion des erreurs robuste
- Limitation des accès DynamoDB par IAM
- Chiffrement des données en transit et au repos

### Performances
- Architecture asynchrone avec asyncio
- Cache LRU pour les configurations
- Optimisation des requêtes DynamoDB
- Compression et mise en cache HTTP

## [0.1.0] - 2025-05-01

### Ajouté
- Version initiale du chatbot
- Intégration basique Telegram + Mistral AI
- Configuration simple via variables d'environnement
- Déploiement manuel sur serveur

---

## Conventions de versioning

Ce projet suit le [Semantic Versioning](https://semver.org/lang/fr/) :

- **MAJOR** (X.0.0) : Changements incompatibles de l'API
- **MINOR** (X.Y.0) : Nouvelles fonctionnalités rétrocompatibles
- **PATCH** (X.Y.Z) : Corrections de bugs rétrocompatibles

### Types de changements

- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Modifications des fonctionnalités existantes
- **Déprécié** : Fonctionnalités bientôt supprimées
- **Supprimé** : Fonctionnalités supprimées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Améliorations de sécurité
