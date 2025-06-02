# Ce script lance tous les composants nécessaires pour un environnement de développement local

$ErrorActionPreference = "Stop"

# Vérifier si Java est installé
try {
    $javaVersion = java -version 2>&1
    Write-Host "Java est installé: $javaVersion"
} catch {
    Write-Host "Java n'est pas installé. Veuillez installer Java avant de continuer."
    exit 1
}

# Vérifier si l'environnement virtuel existe
if (-not (Test-Path ".\venv")) {
    Write-Host "Création de l'environnement virtuel Python..."
    python -m venv venv
}

# Activer l'environnement virtuel et installer les dépendances
Write-Host "Activation de l'environnement virtuel et installation des dépendances..."
& .\venv\Scripts\activate
pip install -r requirements.txt

# Vérifier si le fichier .env existe
if (-not (Test-Path ".\.env")) {
    Write-Host "Le fichier .env n'existe pas. Création à partir de .env.example..."
    if (Test-Path ".\.env.example") {
        Copy-Item .\.env.example .\.env
        Write-Host "Fichier .env créé. Veuillez le modifier avec vos propres valeurs."
    } else {
        Write-Host "Le fichier .env.example n'existe pas. Veuillez créer un fichier .env manuellement."
    }
}

# Demander à l'utilisateur quelle action effectuer
Write-Host "`nQue souhaitez-vous faire ?"
Write-Host "1. Lancer DynamoDB Local"
Write-Host "2. Créer la table DynamoDB locale"
Write-Host "3. Configurer le webhook Telegram avec ngrok"
Write-Host "4. Lancer l'application FastAPI"
Write-Host "5. Tout lancer (DynamoDB + Application)"
$choice = Read-Host "Entrez votre choix (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`nLancement de DynamoDB Local..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& .\setup_local_dynamo.ps1"
    }
    "2" {
        Write-Host "`nCréation de la table DynamoDB locale..."
        mkdir -p scripts
        if (-not (Test-Path ".\scripts")) {
            New-Item -ItemType Directory -Path ".\scripts"
        }
        python .\scripts\create_local_table.py
    }
    "3" {
        Write-Host "`nConfiguration du webhook Telegram avec ngrok..."
        python .\scripts\setup_ngrok_webhook.py
    }
    "4" {
        Write-Host "`nLancement de l'application FastAPI..."
        uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    }
    "5" {
        Write-Host "`nLancement de DynamoDB Local..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& .\setup_local_dynamo.ps1"
        
        Write-Host "`nAttente du démarrage de DynamoDB (5 secondes)..."
        Start-Sleep -Seconds 5
        
        Write-Host "`nCréation de la table DynamoDB locale..."
        python .\scripts\create_local_table.py
        
        Write-Host "`nConfiguration du webhook Telegram avec ngrok..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "python .\scripts\setup_ngrok_webhook.py"
        
        Start-Sleep -Seconds 3
        
        Write-Host "`nLancement de l'application FastAPI..."
        uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    }
    default {
        Write-Host "Choix invalide. Sortie du script."
    }
}
