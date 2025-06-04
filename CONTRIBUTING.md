# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer au projet **Chatbot Telegram avec Mistral AI** ! Ce guide vous explique comment participer efficacement au développement.

## 📋 Table des matières

- [🚀 Pour commencer](#-pour-commencer)
- [🔧 Environnement de développement](#-environnement-de-développement)
- [📝 Standards de code](#-standards-de-code)
- [🔀 Workflow Git](#-workflow-git)
- [🧪 Tests](#-tests)
- [📖 Documentation](#-documentation)
- [🐛 Signaler des bugs](#-signaler-des-bugs)
- [💡 Proposer des fonctionnalités](#-proposer-des-fonctionnalités)
- [👥 Communauté](#-communauté)

## 🚀 Pour commencer

### Prérequis

- **Python 3.12+**
- **Git**
- **Compte AWS** (pour les tests de déploiement)
- **Bot Telegram** (token obtenu via @BotFather)
- **Clé API Mistral AI**

### Fork et Clone

```bash
# 1. Fork le repository sur GitHub
# 2. Clone votre fork
git clone https://github.com/VOTRE-USERNAME/chatbot.git
cd chatbot

# 3. Ajouter le repository original comme upstream
git remote add upstream https://github.com/kybaloo/chatbot.git
```

## 🔧 Environnement de développement

### Installation rapide

```powershell
# Méthode PowerShell (recommandée pour Windows)
.\build.ps1 venv
.\build.ps1 install

# Méthode Make (Linux/macOS)
make venv
make install

# Méthode manuelle
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### Configuration

```powershell
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos clés API
# - TELEGRAM_BOT_TOKEN=votre_token_telegram
# - MISTRAL_API_KEY=votre_clé_mistral
# - etc.
```

### Démarrage développement

```powershell
# PowerShell
.\build.ps1 run-dev

# Make
make run-dev

# Manuel
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📝 Standards de code

### Style Python

Nous utilisons des outils automatisés pour maintenir la qualité du code :

```powershell
# Formatage automatique
.\build.ps1 format  # ou make format

# Vérification du style
.\build.ps1 lint    # ou make lint

# Type checking
.\build.ps1 mypy    # ou make mypy
```

### Conventions

#### Nommage
- **Classes** : `PascalCase` (ex: `ConversationService`)
- **Fonctions/variables** : `snake_case` (ex: `get_user_conversations`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `MAX_MESSAGE_LENGTH`)
- **Fichiers** : `snake_case.py` (ex: `conversation_service.py`)

#### Structure des modules
```python
"""
Description du module
"""

# 1. Imports standard library
import os
import logging

# 2. Imports third-party
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Imports locaux
from .config.settings import env_vars
from .utils.logger import log_info

# 4. Constants
MAX_RETRIES = 3

# 5. Classes et fonctions
class ExampleClass:
    """Documentation de la classe"""
    pass
```

#### Documentation

Utilisez les docstrings Google style :

```python
def example_function(param1: str, param2: int) -> bool:
    """Fonction d'exemple qui fait quelque chose.
    
    Args:
        param1: Description du premier paramètre
        param2: Description du deuxième paramètre
        
    Returns:
        True si succès, False sinon
        
    Raises:
        ValueError: Si param2 est négatif
        
    Example:
        >>> example_function("test", 42)
        True
    """
    if param2 < 0:
        raise ValueError("param2 must be positive")
    return True
```

## 🔀 Workflow Git

### Branches

- **`main`** : Production stable
- **`develop`** : Développement en cours
- **`feature/nom-fonctionnalité`** : Nouvelles fonctionnalités
- **`bugfix/nom-bug`** : Corrections de bugs
- **`hotfix/nom-correctif`** : Correctifs urgents

### Processus de contribution

1. **Synchroniser avec upstream**
   ```bash
   git checkout develop
   git pull upstream develop
   ```

2. **Créer une branche feature**
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```

3. **Développer et tester**
   ```powershell
   # Faire vos modifications
   
   # Tester
   .\build.ps1 test
   .\build.ps1 lint
   .\build.ps1 format
   ```

4. **Commit avec messages clairs**
   ```bash
   git add .
   git commit -m "feat: ajouter support pour les messages vocaux
   
   - Implémenter la conversion speech-to-text
   - Ajouter gestion des fichiers audio
   - Mettre à jour les tests
   
   Fixes #123"
   ```

5. **Push et Pull Request**
   ```bash
   git push origin feature/nouvelle-fonctionnalite
   # Puis créer une PR sur GitHub
   ```

### Format des messages de commit

Nous utilisons la convention [Conventional Commits](https://www.conventionalcommits.org/) :

```
type(scope): description courte

Description plus détaillée si nécessaire

- Point important 1
- Point important 2

Fixes #123
```

**Types supportés :**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation uniquement
- `style`: Formatage, pas de changement de logique
- `refactor`: Refactoring sans changement de fonctionnalité
- `test`: Ajout ou modification de tests
- `chore`: Tâches de maintenance

## 🧪 Tests

### Structure des tests

```
tests/
├── unit/           # Tests unitaires
├── integration/    # Tests d'intégration
├── e2e/           # Tests end-to-end
└── fixtures/      # Données de test
```

### Exécution des tests

```powershell
# Tous les tests
.\build.ps1 test

# Tests unitaires uniquement
.\build.ps1 test-unit

# Tests d'intégration
.\build.ps1 test-integration

# Avec couverture
.\build.ps1 test-coverage
```

### Écriture de tests

```python
import pytest
from unittest.mock import Mock, patch
from src.services.ai_service import AIService

class TestAIService:
    """Tests pour le service IA"""
    
    @pytest.fixture
    def ai_service(self):
        """Fixture pour créer un service IA"""
        return AIService()
    
    def test_generate_response_success(self, ai_service):
        """Test la génération réussie d'une réponse"""
        # Arrange
        message = "Bonjour"
        
        # Act
        response = ai_service.generate_response(message)
        
        # Assert
        assert response is not None
        assert len(response) > 0
        
    @patch('src.services.ai_service.MistralClient')
    def test_generate_response_with_mock(self, mock_client, ai_service):
        """Test avec mock pour isoler les dépendances externes"""
        # Arrange
        mock_response = Mock()
        mock_response.choices[0].message.content = "Bonjour !"
        mock_client.return_value.chat.return_value = mock_response
        
        # Act
        result = ai_service.generate_response("Hello")
        
        # Assert
        assert result == "Bonjour !"
```

### Coverage minimum

- **Nouveau code** : 90% minimum
- **Code existant** : Maintenir ou améliorer
- **Services critiques** : 95% minimum
- **Utils/helpers** : 85% minimum

## 📖 Documentation

### README et guides

- Mettre à jour le README.md si nécessaire
- Ajouter des exemples d'utilisation
- Documenter les nouvelles APIs
- Mettre à jour le CHANGELOG.md

### Code documentation

- Docstrings pour toutes les fonctions publiques
- Comments pour la logique complexe
- Type hints obligatoires
- Exemples d'utilisation dans les docstrings

### API Documentation

L'API est auto-documentée via FastAPI/OpenAPI. Après modifications :

1. Démarrer le serveur
2. Visiter `http://localhost:8000/docs`
3. Vérifier que la documentation est correcte

## 🐛 Signaler des bugs

### Template d'issue

Utilisez le template GitHub fourni ou incluez :

1. **Description claire** du problème
2. **Étapes pour reproduire**
3. **Comportement attendu vs réel**
4. **Informations d'environnement** :
   - OS et version
   - Version Python
   - Version des dépendances clés
5. **Logs/screenshots** si pertinents

### Labels

- `bug` : Bug confirmé
- `enhancement` : Amélioration
- `documentation` : Problème de doc
- `good first issue` : Bon pour débutants
- `help wanted` : Aide bienvenue

## 💡 Proposer des fonctionnalités

### Avant de proposer

1. Vérifier les issues existantes
2. Discuter dans les discussions GitHub
3. Considérer l'impact sur l'architecture
4. Évaluer la complexité

### Template de proposition

1. **Problème résolu** : Quel besoin ?
2. **Solution proposée** : Comment ?
3. **Alternatives considérées**
4. **Impact** : Breaking changes ?
5. **Implémentation** : Plan d'approche

### Roadmap

Consultez les [milestones GitHub](https://github.com/kybaloo/chatbot/milestones) pour voir les priorités.

## 👥 Communauté

### Code de conduite

Ce projet adhère au [Contributor Covenant](https://www.contributor-covenant.org/). En participant, vous acceptez de respecter ce code.

### Communication

- **Issues GitHub** : Bugs et fonctionnalités
- **Discussions GitHub** : Questions générales
- **Pull Requests** : Review de code

### Recognition

Les contributeurs sont reconnus dans :
- Le fichier `CONTRIBUTORS.md`
- Les release notes
- Le README principal

---

## 📞 Besoin d'aide ?

- 📖 **Documentation** : Consultez le README et les guides
- 💬 **Discussions** : [GitHub Discussions](https://github.com/kybaloo/chatbot/discussions)
- 🐛 **Bugs** : [GitHub Issues](https://github.com/kybaloo/chatbot/issues)

Merci de contribuer à rendre ce projet encore meilleur ! 🚀
