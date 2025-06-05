---
name: 🔀 Pull Request
about: Template pour soumettre une Pull Request
title: ''
labels: ''
assignees: kybaloo

---

## 📋 Description

### 🎯 Problème résolu
<!-- Décrivez le problème que cette PR résout -->
- Fixes #(issue_number)
- Résout le problème de...

### 💡 Solution proposée
<!-- Décrivez votre solution -->
- Implémente...
- Modifie...
- Ajoute...

## 🔄 Type de changement

<!-- Cochez les types de changements pertinents -->
- [ ] 🐛 **Bug fix** (changement non-breaking qui corrige un problème)
- [ ] ✨ **Nouvelle fonctionnalité** (changement non-breaking qui ajoute une fonctionnalité)
- [ ] 💥 **Breaking change** (changement qui pourrait casser des fonctionnalités existantes)
- [ ] 📚 **Documentation** (mise à jour de documentation uniquement)
- [ ] 🔧 **Maintenance** (refactoring, amélioration de code)
- [ ] 🧪 **Tests** (ajout ou modification de tests)

## 🧪 Tests effectués

### ✅ Tests automatisés
- [ ] Tests unitaires passent (`make test-unit`)
- [ ] Tests d'intégration passent (`make test-integration`)
- [ ] Linting passent (`make lint`)
- [ ] Formatage appliqué (`make format`)

### 🔍 Tests manuels
<!-- Décrivez les tests que vous avez effectués -->
- [ ] Testé localement
- [ ] Testé sur environnement de dev
- [ ] Vérifié l'impact sur les fonctionnalités existantes

### 📊 Couverture de tests
- [ ] Les nouveaux tests maintiennent la couverture minimale (80%)
- [ ] Tous les cas de test critiques sont couverts

## 📝 Checklist

### 🔧 Code
- [ ] Mon code suit les conventions du projet (PEP8, docstrings)
- [ ] J'ai effectué une auto-review de mon code
- [ ] J'ai commenté les parties complexes de mon code
- [ ] Mes changements ne génèrent pas de nouveaux warnings

### 📖 Documentation
- [ ] J'ai mis à jour la documentation correspondante
- [ ] J'ai ajouté des docstrings pour les nouvelles fonctions
- [ ] J'ai mis à jour le CHANGELOG.md si nécessaire

### 🛡️ Sécurité
- [ ] Mon code ne contient pas de secrets hardcodés
- [ ] J'ai vérifié les implications de sécurité de mes changements
- [ ] Les nouvelles dépendances sont auditées

## 📱 Captures d'écran (si applicable)

<!-- Ajoutez des captures d'écran pour illustrer les changements UI -->

## 🔗 Issues liées

<!-- Listez les issues liées à cette PR -->
- Closes #
- Related to #

## 📋 Notes supplémentaires

<!-- Ajoutez toute information supplémentaire pour les reviewers -->

---

### 👥 Pour les reviewers

#### 🔍 Points d'attention
- [ ] Vérifier la logique métier
- [ ] Valider les tests
- [ ] Confirmer la documentation
- [ ] Tester manuellement si nécessaire

#### 🎯 Focus de review
<!-- Indiquez sur quoi les reviewers devraient se concentrer -->
- Performance
- Sécurité  
- Lisibilité du code
- Tests
