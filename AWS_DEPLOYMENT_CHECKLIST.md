# Liste de vérification pour le déploiement AWS

Utilisez cette liste de vérification pour vous assurer que toutes les étapes nécessaires sont complétées avant et après le déploiement sur AWS.

## Avant le déploiement

- [ ] Les variables d'environnement sont configurées dans le fichier `.env`
- [ ] Le code a passé tous les tests unitaires (`make test`)
- [ ] L'image Docker a été construite et testée localement (`docker build -t chatbot:latest .`)
- [ ] Le repository ECR a été créé
- [ ] L'image Docker a été poussée vers ECR
- [ ] La paire de clés EC2 existe dans la région cible
- [ ] Les identifiants AWS sont correctement configurés

## Configuration AWS requise

- [ ] Compte AWS avec accès administrateur
- [ ] AWS CLI installé et configuré
- [ ] SAM CLI installé et configuré
- [ ] Accès à ECR, Lambda, DynamoDB, EC2, API Gateway
- [ ] Quota suffisant pour les ressources EC2 dans la région cible

## Ressources à déployer

- [ ] Table DynamoDB avec clés de partition et de tri
- [ ] Instance EC2 pour le bot Telegram
- [ ] Fonction Lambda pour l'API
- [ ] API Gateway connectée à Lambda
- [ ] Rôles IAM avec les autorisations nécessaires
- [ ] Groupe de sécurité EC2 avec les ports ouverts

## Après le déploiement

- [ ] Vérifier que toutes les ressources ont été créées dans AWS Console
- [ ] Vérifier que l'instance EC2 est en cours d'exécution
- [ ] Vérifier que le webhook Telegram est correctement configuré
- [ ] Vérifier que l'API répond correctement
- [ ] Vérifier que les données sont bien enregistrées dans DynamoDB
- [ ] Configurer des alarmes CloudWatch pour la surveillance
- [ ] Vérifier les logs pour détecter d'éventuelles erreurs

## Étapes de test

- [ ] Envoyer un message au bot Telegram et vérifier la réponse
- [ ] Utiliser l'API pour créer une nouvelle conversation
- [ ] Vérifier que les conversations sont correctement sauvegardées
- [ ] Tester le comportement en cas de redémarrage de l'EC2
- [ ] Vérifier les performances sous charge (si applicable)

## Plan de rollback

Si le déploiement échoue ou présente des problèmes:

1. Restaurer le stack CloudFormation précédent:
   ```
   aws cloudformation continue-update-rollback --stack-name chatbot-stack-dev
   ```

2. Si nécessaire, revenir à l'image Docker précédente:
   ```
   aws ecr batch-delete-image --repository-name dev-chatbot --image-ids imageTag=latest
   ```

3. Documenter l'incident et les actions entreprises
