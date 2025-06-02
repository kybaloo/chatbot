# Architecture du Chatbot

Ce document décrit l'architecture du chatbot, ses composants principaux et leurs interactions.

## Architecture Globale

Le projet est organisé selon une architecture en couches avec séparation des responsabilités :

```
chatbot/
├── src/                   # Code source principal
│   ├── api/               # Couche API (endpoints FastAPI)
│   ├── bot/               # Intégration avec Telegram
│   ├── config/            # Configuration de l'application
│   ├── models/            # Modèles de données
│   ├── repositories/      # Couche d'accès aux données
│   ├── services/          # Logique métier
│   └── utils/             # Utilitaires communs
├── infrastructure/        # Infrastructure AWS CloudFormation
├── tests/                 # Tests unitaires et d'intégration
```

## Diagramme de Composants

```
┌────────────────┐     ┌─────────────────┐     ┌────────────────┐
│  API (FastAPI) │     │ Bot (Telegram)  │     │  CLI (Future)  │
└───────┬────────┘     └────────┬────────┘     └────────┬───────┘
        │                       │                       │
        v                       v                       v
┌─────────────────────────────────────────────────────────────┐
│                       Services Layer                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐   │
│  │ConversationSvc  │ │    AISvc        │ │   UserSvc    │   │
│  └────────┬────────┘ └────────┬────────┘ └──────┬───────┘   │
└───────────┼──────────────────┬────────────────┬─────────────┘
            │                  │                │
            v                  v                v
┌─────────────────────────────────────────────────────────────┐
│                     Repository Layer                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐   │
│  │ConversationRepo │ │  DynamoDBRepo   │ │  UserRepo    │   │
│  └────────┬────────┘ └────────┬────────┘ └──────┬───────┘   │
└───────────┼──────────────────┬────────────────┬─────────────┘
            │                  │                │
            v                  v                v
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐   │
│  │    DynamoDB     │ │     S3          │ │   Other DBs  │   │
│  └─────────────────┘ └─────────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Détails des Composants

### 1. Couche Présentation

#### API REST (FastAPI)
- Expose des endpoints HTTP pour interagir avec le chatbot
- Gère la validation des requêtes et les réponses
- Routes principales: `/chat`, `/conversations/{user_id}`, etc.

#### Bot Telegram
- Intègre avec l'API Telegram via webhooks
- Gère les commandes utilisateur (`/start`, `/help`, `/history`, etc.)
- Fournit une interface conviviale pour les utilisateurs Telegram

### 2. Couche Services

#### ConversationService
- Gère la logique métier liée aux conversations
- Crée, récupère, met à jour et supprime des conversations
- Ajoute des messages aux conversations

#### AIService
- Intègre avec l'API Mistral AI
- Gère les requêtes de chat et les réponses
- Configure les paramètres du modèle

#### UserService (à venir)
- Gérera les profils utilisateurs et les préférences
- Authentification et autorisation

### 3. Couche Repositories

#### ConversationRepository
- Abstrait l'accès aux données pour les conversations
- Implémente les opérations CRUD pour les conversations
- Utilise DynamoDB comme stockage principal

#### UserRepository (à venir)
- Gèrera l'accès aux données utilisateur

### 4. Couche Modèles

#### Conversation & Message
- Modèles de données pour représenter les conversations et messages
- Inclut la logique métier spécifique aux entités

#### User
- Représente un utilisateur du système
- Stocke les préférences et métadonnées

#### AIModel
- Configuration et paramètres des modèles d'IA
- Modèles prédéfinis pour différentes utilisations

### 5. Couche Utilitaires

#### Logger
- Configuration du logging centralisée
- Fonctions d'aide pour le logging

#### Helpers
- Fonctions utilitaires diverses (formatage, parsing, etc.)

## Flux de Données

1. **Requête de chat via API REST**:
   ```
   Client → API → ConversationService → AIService → Repository → DynamoDB
   ```

2. **Message Telegram**:
   ```
   Telegram → Webhook → TelegramBot → ConversationService → AIService → Repository → DynamoDB
   ```

3. **Récupération d'historique**:
   ```
   Client → API → ConversationService → Repository → DynamoDB → Client
   ```

## Aspects de Conception

### Pattern Repository
- Abstraction de la couche données
- Facilite les tests unitaires
- Permet de changer la source de données sans modifier la logique métier

### Injection de Dépendances
- Les services reçoivent leurs dépendances via le constructeur
- Facilite les tests et la substitution des composants

### Architecture en Couches
- Séparation claire des responsabilités
- Facilite la maintenance et l'évolution du code

### Modèles de Données Riches
- Les modèles contiennent la logique métier liée à l'entité
- Les services orchestrent les interactions entre modèles

## Sécurité

- Variables d'environnement pour les secrets
- Structure de contrôle d'accès pour les données (à venir)
- Validation des données d'entrée via Pydantic
- Gestion des erreurs et exceptions robuste

## Extensions Futures

- Interface Web pour l'administration
- Support multimodal (images, audio)
- Intégration avec d'autres plateformes de messagerie
- Système de plugins pour étendre les fonctionnalités
