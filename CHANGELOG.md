# Changelog et Notes de Version

## Version 1.0.0 - Juin 2025

### Architecture refactorée (Majeur)

- Restructuration complète du projet avec une architecture en couches
- Implémentation du pattern Repository pour l'accès aux données
- Implémentation de la couche Service pour la logique métier
- Modèles de données enrichis avec des méthodes utilitaires
- Centralisation de la configuration avec pydantic-settings
- Amélioration du logging et des utilitaires

### Nouvelles fonctionnalités

- Gestion avancée des conversations avec sauvegarde dans DynamoDB
- Support de différents modèles Mistral AI avec paramètres configurables
- Gestion des préférences utilisateur
- API REST complète avec FastAPI
- Webhook Telegram amélioré avec gestion avancée des commandes

### Documentation

- Documentation complète de l'architecture (ARCHITECTURE.md)
- README mis à jour
- Tests unitaires et d'intégration

### Comment utiliser la nouvelle architecture

#### Exécution de l'application

```bash
# Démarrer l'application en mode développement
make run-dev

# Ou directement avec uvicorn
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

#### Tests

```bash
# Exécuter tous les tests
make test

# Exécuter uniquement les tests unitaires
make test-unit

# Exécuter uniquement les tests d'intégration
make test-integration
```

#### Autres commandes utiles

```bash
# Formatter le code avec black
make format

# Vérifier la qualité du code avec flake8
make lint

# Générer la documentation
make docs
```

### Prochaines étapes

- Implémentation d'une interface utilisateur Web pour l'administration
- Support multimodal (images, audio)
- Système de plugins pour étendre les fonctionnalités
- Amélioration de la sécurité et des performances
- Déploiement automatisé via CI/CD
- Intégration avec d'autres plateformes de messagerie
