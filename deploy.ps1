param (
    [Parameter(Mandatory = $true)]
    [string]$env,
    [string]$region = "eu-west-3",
    [switch]$skipBuild = $false
)

# Vérifier les variables d'environnement requises
if (-not $env:MISTRAL_API_KEY) {
    Write-Host "ERROR: MISTRAL_API_KEY environment variable must be set" -ForegroundColor Red
    exit 1
}

if (-not $env:TELEGRAM_BOT_TOKEN) {
    Write-Host "ERROR: TELEGRAM_BOT_TOKEN environment variable must be set" -ForegroundColor Red
    exit 1
}

# Vérifier si SAM CLI est installé
try {
    $samVersion = & sam --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "AWS SAM CLI is not installed. Please install it first:" -ForegroundColor Red
        Write-Host "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "AWS SAM CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html" -ForegroundColor Yellow
    exit 1
}

# Afficher des informations sur le déploiement
Write-Host "Deploying to $env" -ForegroundColor Blue

# Construire le projet s'il n'est pas déjà construit
if (-not $skipBuild) {
    Write-Host "Building the project with SAM..." -ForegroundColor Blue
    sam build --template infrastructure/template.yaml
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# Exécuter la commande de déploiement SAM
sam deploy --resolve-s3 --template-file .aws-sam/build/template.yaml --stack-name "multi-stack-$env" `
     --capabilities CAPABILITY_IAM --region $region `
     --parameter-overrides `
     ParameterKey=EnvironmentName,ParameterValue=$env `
     ParameterKey=TelegramBotToken,ParameterValue=$env:TELEGRAM_BOT_TOKEN `
     ParameterKey=MistralApiKey,ParameterValue=$env:MISTRAL_API_KEY `
     ParameterKey=TelegramWebhookUrl,ParameterValue=$env:TELEGRAM_WEBHOOK_URL `
     --no-fail-on-empty-changeset

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
} else {
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
}
