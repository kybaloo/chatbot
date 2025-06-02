# Guide de déploiement AWS

Ce document décrit les étapes nécessaires pour déployer l'application ChatBot Telegram sur AWS.

## Prérequis

- Un compte AWS avec les droits d'administrateur
- AWS CLI configuré sur votre machine
- Un token de bot Telegram
- Une clé API Mistral AI
- Une paire de clés EC2 pour l'accès SSH

## Architecture du déploiement

L'application est déployée sur AWS avec les composants suivants :

1. **AWS Lambda** - Pour l'API FastAPI
2. **API Gateway** - Pour exposer les endpoints HTTP de l'API
3. **DynamoDB** - Pour stocker les conversations
4. **EC2** - Pour exécuter le bot Telegram qui nécessite une connexion persistante
5. **ECR** - Pour stocker les images Docker

## Configuration de l'ECR (Elastic Container Registry)

Avant le déploiement, vous devez créer un repository ECR et y pousser l'image Docker :

```powershell
# Connexion à ECR
aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.eu-west-3.amazonaws.com

# Création du repository
aws ecr create-repository --repository-name $env:EnvironmentName-chatbot --region eu-west-3

# Construction de l'image Docker
docker build -t $env:EnvironmentName-chatbot .

# Tag de l'image
docker tag $env:EnvironmentName-chatbot:latest 123456789012.dkr.ecr.eu-west-3.amazonaws.com/$env:EnvironmentName-chatbot:latest

# Push de l'image vers ECR
docker push 123456789012.dkr.ecr.eu-west-3.amazonaws.com/$env:EnvironmentName-chatbot:latest
```

## Déploiement de l'infrastructure

Pour déployer l'infrastructure complète sur AWS, utilisez la commande suivante :

```powershell
# Définition des variables d'environnement
$env:EnvironmentName = "dev" # ou "preprod", "prod"
$env:AWS_REGION = "eu-west-3"
$env:MISTRAL_API_KEY = "votre-cle-api-mistral"
$env:TELEGRAM_BOT_TOKEN = "votre-token-telegram"
$env:WEBHOOK_URL = "" # Laissez vide pour dev, renseignez pour prod

# Déploiement avec SAM CLI
sam deploy --template-file infrastructure/template.yaml `
    --stack-name chatbot-stack-$env:EnvironmentName `
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM `
    --parameter-overrides `
        EnvironmentName=$env:EnvironmentName `
        MistralApiKey=$env:MISTRAL_API_KEY `
        TelegramBotToken=$env:TELEGRAM_BOT_TOKEN `
        WebhookUrl=$env:WEBHOOK_URL `
        KeyPairName="votre-keypair" `
        DockerImageRepository="123456789012.dkr.ecr.eu-west-3.amazonaws.com"
```

## Configuration post-déploiement

Une fois l'infrastructure déployée, vous devez configurer le webhook Telegram :

```powershell
# Récupération de l'URL de l'API Gateway
$ApiUrl = aws cloudformation describe-stacks `
    --stack-name chatbot-stack-$env:EnvironmentName `
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" `
    --output text

# Récupération de l'adresse IP publique de l'instance EC2
$EC2PublicIP = aws cloudformation describe-stacks `
    --stack-name chatbot-stack-$env:EnvironmentName `
    --query "Stacks[0].Outputs[?OutputKey=='EC2PublicIP'].OutputValue" `
    --output text

# Configuration du webhook Telegram
Invoke-WebRequest -Uri "https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/setWebhook?url=http://$EC2PublicIP:8000/$env:TELEGRAM_BOT_TOKEN" -Method GET
```

## Vérification du déploiement

Pour vérifier que tout fonctionne correctement :

1. **Vérifiez l'API** : Accédez à l'URL de l'API Gateway et assurez-vous qu'elle répond avec un message "Hello World"
2. **Vérifiez le bot Telegram** : Envoyez un message à votre bot Telegram et assurez-vous qu'il répond
3. **Vérifiez DynamoDB** : Consultez la table DynamoDB pour vous assurer que les conversations sont enregistrées

## Gestion des déploiements avec Jenkins

Le pipeline Jenkins est configuré pour automatiser le déploiement. Les étapes générales sont :

1. Construction de l'image Docker
2. Push de l'image vers ECR
3. Déploiement de l'infrastructure CloudFormation
4. Configuration du webhook Telegram

## Environnements et variables

| Variable | Dev | PreProd | Prod |
|----------|-----|---------|------|
| EnvironmentName | dev | preprod | prod |
| EC2 Instance Type | t2.micro | t2.small | t2.medium |
| DynamoDB Capacity | 5 RCU/WCU | 10 RCU/WCU | Auto Scaling |
| WebhookUrl | Empty | https://preprod.example.com | https://api.example.com |

## Surveillance et maintenance

Pour surveiller votre application :

1. **CloudWatch** : Configurez des alarmes pour surveiller les métriques de l'application
2. **Logs** : Consultez les journaux dans CloudWatch Logs
3. **Mises à jour** : Redéployez l'infrastructure pour appliquer des mises à jour

## Résolution des problèmes courants

### Le bot Telegram ne répond pas

- Vérifiez que l'instance EC2 est en cours d'exécution
- Vérifiez que le webhook est correctement configuré
- Vérifiez les journaux Docker sur l'instance EC2

### L'API ne répond pas

- Vérifiez que la fonction Lambda est correctement déployée
- Vérifiez les journaux CloudWatch de la fonction Lambda
- Vérifiez la configuration de l'API Gateway

### Problèmes avec DynamoDB

- Vérifiez les autorisations IAM
- Vérifiez les limites de capacité de la table
- Vérifiez les journaux d'accès à DynamoDB
