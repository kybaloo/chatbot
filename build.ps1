# ====================================================================
# Build Script for Chatbot Telegram avec Mistral AI
# PowerShell script équivalent au Makefile pour Windows
# ====================================================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [string]$env = "kybaloo",
    [string]$AWS_REGION = "eu-west-3",
    [string]$TELEGRAM_BOT_TOKEN = "",
    [string]$MISTRAL_API_KEY = "",
    [string]$WEBHOOK_URL = ""
)

# Colors for output (using Write-Host -ForegroundColor for better compatibility)
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

# Get current version
function Get-CurrentVersion {
    if (Test-Path "version") {
        return Get-Content "version" -Raw | ForEach-Object { $_.Trim() }
    }
    return "1.0.0"
}

$VERSION = Get-CurrentVersion
$PROJECT_NAME = "chatbot-telegram-mistral"

function Show-Help {
    Write-ColorText "🤖 Chatbot Telegram avec Mistral AI - v$VERSION" "Cyan"
    Write-Host ""
    Write-ColorText "Commandes disponibles:" "Green"
    Write-Host "  help                 " -NoNewline; Write-ColorText "Afficher cette aide" "White"
    Write-Host "  version              " -NoNewline; Write-ColorText "Afficher la version actuelle" "White"
    Write-Host "  bump-major           " -NoNewline; Write-ColorText "Augmenter la version majeure (1.0.0 -> 2.0.0)" "White"
    Write-Host "  bump-minor           " -NoNewline; Write-ColorText "Augmenter la version mineure (1.0.0 -> 1.1.0)" "White"
    Write-Host "  bump-patch           " -NoNewline; Write-ColorText "Augmenter la version de patch (1.0.0 -> 1.0.1)" "White"
    Write-Host "  clean                " -NoNewline; Write-ColorText "Nettoyer les artefacts de build" "White"
    Write-Host "  venv                 " -NoNewline; Write-ColorText "Créer un environnement virtuel" "White"
    Write-Host "  install              " -NoNewline; Write-ColorText "Installer les dépendances" "White"
    Write-Host "  build                " -NoNewline; Write-ColorText "Construire le projet" "White"
    Write-Host "  run-dev              " -NoNewline; Write-ColorText "Lancer en mode développement" "White"
    Write-Host "  format               " -NoNewline; Write-ColorText "Formater le code avec Black" "White"    Write-Host "  lint                 " -NoNewline; Write-ColorText "Vérifier le code avec Flake8" "White"
    Write-Host "  validate             " -NoNewline; Write-ColorText "Valider la configuration du projet" "White"
    Write-Host "  validate-pipeline    " -NoNewline; Write-ColorText "Valider les améliorations du pipeline Jenkins" "White"
    Write-Host "  test                 " -NoNewline; Write-ColorText "Exécuter tous les tests" "White"
    Write-Host "  test-unit            " -NoNewline; Write-ColorText "Exécuter les tests unitaires" "White"
    Write-Host "  test-integration     " -NoNewline; Write-ColorText "Exécuter les tests d'intégration" "White"
    Write-Host "  deploy               " -NoNewline; Write-ColorText "Déployer sur AWS" "White"
    Write-Host ""
    Write-ColorText "Exemples:" "Green"
    Write-Host "  .\build.ps1 help"
    Write-Host "  .\build.ps1 version"
    Write-Host "  .\build.ps1 bump-patch"
    Write-Host "  .\build.ps1 install"
    Write-Host "  .\build.ps1 run-dev"
}

function Show-Version {
    Write-ColorText "Version actuelle: $VERSION" "Green"
}

function Bump-Version {
    param([string]$Type)
    
    $versionParts = $VERSION.Split('.')
    $major = [int]$versionParts[0]
    $minor = [int]$versionParts[1]
    $patch = [int]$versionParts[2]
    
    switch ($Type) {
        "major" {
            $major++
            $minor = 0
            $patch = 0
            Write-ColorText "Augmentation de la version majeure..." "Cyan"
        }
        "minor" {
            $minor++
            $patch = 0
            Write-ColorText "Augmentation de la version mineure..." "Cyan"
        }
        "patch" {
            $patch++
            Write-ColorText "Augmentation de la version de patch..." "Cyan"
        }
    }
    
    $newVersion = "$major.$minor.$patch"
    Set-Content -Path "version" -Value $newVersion -NoNewline
    Write-ColorText "Version mise à jour vers: $newVersion" "Green"
}

function Clean-Project {
    Write-ColorText "Nettoyage du projet..." "Cyan"
    
    # Remove virtual environments
    if (Test-Path "venv") { Remove-Item "venv" -Recurse -Force }
    if (Test-Path ".venv") { Remove-Item ".venv" -Recurse -Force }
    
    # Remove Python cache
    Get-ChildItem -Path . -Name "__pycache__" -Recurse | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Name "*.pyc" -Recurse | Remove-Item -Force
    
    # Remove build artifacts
    if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
    if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
    Get-ChildItem -Path . -Name "*.egg-info" -Recurse | Remove-Item -Recurse -Force
    
    # Remove test artifacts
    if (Test-Path ".pytest_cache") { Remove-Item ".pytest_cache" -Recurse -Force }
    if (Test-Path ".mypy_cache") { Remove-Item ".mypy_cache" -Recurse -Force }
    if (Test-Path ".coverage") { Remove-Item ".coverage" -Force }
    if (Test-Path "htmlcov") { Remove-Item "htmlcov" -Recurse -Force }
    
    # Remove AWS SAM artifacts
    if (Test-Path ".aws-sam") { Remove-Item ".aws-sam" -Recurse -Force }
    
    Write-ColorText "Projet nettoyé!" "Green"
}

function Create-Venv {
    Clean-Project
    Write-ColorText "Création de l'environnement virtuel..." "Cyan"
    python -m venv .venv
    Write-ColorText "Environnement virtuel créé dans .venv" "Green"
}

function Install-Dependencies {
    Write-ColorText "Installation des dépendances..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/pip.exe" install -r requirements.txt
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé. Exécutez d'abord 'venv'" "Red"
        exit 1
    }
    Write-ColorText "Dépendances installées!" "Green"
}

function Build-Project {
    Write-ColorText "Construction du projet..." "Cyan"
    if (Get-Command sam -ErrorAction SilentlyContinue) {
        sam build --use-container -t infrastructure/template.yaml
    }
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        docker build -t chatbot:latest .
    }
    Write-ColorText "Projet construit!" "Green"
}

function Run-Dev {
    Write-ColorText "Lancement en mode développement..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/uvicorn.exe" src.main:app --reload --host 0.0.0.0 --port 8000
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé" "Red"
        exit 1
    }
}

function Format-Code {
    Write-ColorText "Formatage du code avec Black..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/python.exe" -m black src tests
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé" "Red"
        exit 1
    }
    Write-ColorText "Code formaté!" "Green"
}

function Lint-Code {
    Write-ColorText "Vérification du code avec Flake8..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/python.exe" -m flake8 src tests
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé" "Red"
        exit 1
    }
    Write-ColorText "Code vérifié!" "Green"
}

function Validate-Project {
    Write-ColorText "Validation du projet..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/python.exe" scripts/validate_project_complete.py
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé" "Red"
        exit 1
    }
}

function Validate-Pipeline {
    Write-ColorText "Validation des améliorations du pipeline..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/python.exe" scripts/validate_pipeline_improvements.py
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé" "Red"
        exit 1
    }
}

function Run-Tests {
    Write-ColorText "Exécution des tests..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/python.exe" -m pytest
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé" "Red"
        exit 1
    }
}

function Run-Unit-Tests {
    Write-ColorText "Exécution des tests unitaires..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/python.exe" -m pytest tests/models tests/repositories tests/services
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé" "Red"
        exit 1
    }
}

function Run-Integration-Tests {
    Write-ColorText "Exécution des tests d'intégration..." "Cyan"
    if (Test-Path ".venv/Scripts/activate.ps1") {
        & ".venv/Scripts/python.exe" -m pytest tests/test_api_integration.py
    } else {
        Write-ColorText "Erreur: Environnement virtuel non trouvé" "Red"
        exit 1
    }
}

function Deploy-Project {
    Write-ColorText "Déploiement vers $env" "Cyan"
    
    if ([string]::IsNullOrEmpty($MISTRAL_API_KEY)) {
        Write-ColorText "ERREUR: La variable d'environnement MISTRAL_API_KEY doit être définie" "Red"
        exit 1
    }
    
    if ([string]::IsNullOrEmpty($TELEGRAM_BOT_TOKEN)) {
        Write-ColorText "ERREUR: La variable d'environnement TELEGRAM_BOT_TOKEN doit être définie" "Red"
        exit 1
    }
    
    sam deploy --resolve-s3 --template-file .aws-sam/build/template.yaml --stack-name "multi-stack-$env" `
        --capabilities CAPABILITY_IAM --region $AWS_REGION `
        --parameter-overrides `
        ParameterKey=EnvironmentName,ParameterValue=$env `
        ParameterKey=TelegramBotToken,ParameterValue=$TELEGRAM_BOT_TOKEN `
        ParameterKey=MistralApiKey,ParameterValue=$MISTRAL_API_KEY `
        ParameterKey=TelegramWebhookUrl,ParameterValue=$WEBHOOK_URL `
        --no-fail-on-empty-changeset
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "version" { Show-Version }
    "bump-major" { Bump-Version "major" }
    "bump-minor" { Bump-Version "minor" }
    "bump-patch" { Bump-Version "patch" }
    "clean" { Clean-Project }
    "venv" { Create-Venv }
    "install" { Install-Dependencies }
    "build" { Build-Project }
    "run-dev" { Run-Dev }    "format" { Format-Code }    "lint" { Lint-Code }
    "validate" { Validate-Project }
    "validate-pipeline" { Validate-Pipeline }
    "test" { Run-Tests }
    "test-unit" { Run-Unit-Tests }
    "test-integration" { Run-Integration-Tests }
    "deploy" { Deploy-Project }    default { 
        Write-ColorText "Commande inconnue: $Command" "Red"
        Show-Help 
    }
}
