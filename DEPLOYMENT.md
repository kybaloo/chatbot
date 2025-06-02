# Guide de Déploiement

Ce document explique la procédure de déploiement du chatbot avec notre nouvelle architecture.

## Architecture de Déploiement

Notre application utilise une architecture moderne avec les composants suivants :

- **FastAPI** avec **Mangum** pour la compatibilité AWS Lambda
- **AWS Lambda** pour le traitement des requêtes API
- **API Gateway** pour exposer les endpoints
- **DynamoDB** pour le stockage des conversations
- **EC2** pour héberger le bot Telegram en mode webhook
- **CloudFormation** pour l'infrastructure as code
- **Jenkins** pour l'intégration et le déploiement continus

## Flux de Déploiement

1. Le code est poussé vers le dépôt Git
2. Jenkins détecte les changements et déclenche le pipeline
3. Les tests et vérifications de qualité sont exécutés
4. L'application est construite et empaquetée
5. L'infrastructure est déployée via CloudFormation
6. Les tests d'intégration sont exécutés sur l'environnement déployé
7. Le webhook Telegram est configuré (pour prod/preprod)
8. Des notifications sont envoyées pour indiquer le statut du déploiement

## Environnements

Notre application supporte plusieurs environnements :

- **dev** : Pour le développement et les tests
- **preprod** : Pour les tests avant production
- **prod** : Environnement de production

Chaque environnement a sa propre stack CloudFormation et sa propre table DynamoDB.

## Variables d'Environnement

Les variables d'environnement clés pour le déploiement sont :

- `ENV_NAME` : Nom de l'environnement (dev, preprod, prod)
- `AWS_REGION_NAME` : Région AWS pour le déploiement
- `DYNAMO_TABLE` : Nom de la table DynamoDB
- `MISTRAL_API_KEY` : Clé API pour Mistral AI
- `TELEGRAM_BOT_TOKEN` : Token du bot Telegram
- `WEBHOOK_URL` : URL pour le webhook Telegram
- `LOG_LEVEL` : Niveau de log (INFO, DEBUG, etc.)
- `ENABLE_TELEGRAM_BOT` : Active/désactive le bot Telegram
- `CONVERSATION_TTL_DAYS` : Durée de conservation des conversations

## Déploiement Manuel

Pour déployer manuellement l'application :

```bash
# Déployer vers l'environnement de développement
make deploy env=dev

# Déployer vers la préproduction
make deploy env=preprod

# Déployer vers la production
make deploy env=prod
```

## Déploiement via Jenkins

Le déploiement automatisé via Jenkins est déclenché par :

1. Un push sur la branche `dev` pour l'environnement de développement
2. Un push sur la branche `preprod` pour l'environnement de préproduction
3. Un push sur la branche `prod` pour l'environnement de production

## Vérification du Déploiement

Après un déploiement, vous pouvez vérifier l'état de l'application en :

1. Consultant les logs Jenkins
2. Testant les endpoints API
3. Vérifiant le fonctionnement du bot Telegram
4. Contrôlant les métriques CloudWatch

## Rollback

En cas de problème après un déploiement :

1. Vérifiez les logs Jenkins pour identifier l'erreur
2. Effectuez un rollback à la version précédente via CloudFormation :
   ```bash
   aws cloudformation rollback-stack --stack-name chatbot-stack-${env}
   ```
3. Ou déployez à nouveau une version fonctionnelle connue

## Maintenance

Pour la maintenance de l'infrastructure :

1. Les tables DynamoDB ont une TTL configurée à 30 jours pour les conversations
2. Les logs CloudWatch sont conservés selon la politique par défaut
3. Les images Docker obsolètes doivent être nettoyées périodiquement d'ECR

## Surveillance

Notre application est surveillée via :

1. CloudWatch Logs pour les journaux d'application
2. CloudWatch Metrics pour les performances
3. Alertes CloudWatch pour les incidents
4. Notifications Telegram pour les déploiements réussis/échoués
