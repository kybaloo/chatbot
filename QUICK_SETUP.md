# ⚡ Démarrage Ultra-Rapide

**Lancez votre chatbot Telegram en moins de 5 minutes !**

## 🚀 Setup Express (3 commandes)

```powershell
# 1. Clone et setup
git clone https://github.com/kybaloo/chatbot.git && cd chatbot

# 2. Environment et dépendances (Windows)
.\build.ps1 venv && .\build.ps1 install

# 3. Configuration
cp .env.example .env
# ⚠️ Éditez .env avec vos clés API (obligatoire)
```

## 🔑 Configuration minimale

Éditez le fichier `.env` créé :

```env
# 🤖 IA - Obligatoire
MISTRAL_API_KEY=votre_cle_mistral_ici

# 📱 Bot - Obligatoire
TELEGRAM_BOT_TOKEN=votre_token_bot_ici

# ⚙️ Optionnel (valeurs par défaut OK)
ENV_NAME=local
AWS_REGION_NAME=eu-west-3
LOG_LEVEL=INFO
```

### 🔗 Où obtenir les clés ?

- **Mistral API** : [console.mistral.ai](https://console.mistral.ai/) → API Keys
- **Telegram Bot** : Message [@BotFather](https://t.me/BotFather) → `/newbot`

## ▶️ Lancement (1 commande)

```powershell
# Démarrer l'application
.\build.ps1 run-dev
```

✅ **Application prête !**
- API : http://localhost:8000
- Docs : http://localhost:8000/docs
- Testez votre bot sur Telegram !

## 🧪 Test rapide

1. **Bot Telegram** : Cherchez votre bot → `/start`
2. **API Health** : http://localhost:8000/ 
3. **Chat API** :
   ```powershell
   curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"question":"Bonjour","user_id":"test"}'
   ```

## 🐛 Problèmes fréquents

| Problème | Solution |
|----------|----------|
| `❌ python not found` | Installez Python 3.12+ |
| `❌ MISTRAL_API_KEY missing` | Ajoutez votre clé dans `.env` |
| `❌ Bot not responding` | Vérifiez `TELEGRAM_BOT_TOKEN` |
| `❌ Import errors` | `.\build.ps1 install` |

## 📚 Prochaines étapes

- **Configuration avancée** : Consultez [README.md](README.md#configuration)
- **Déploiement AWS** : Guide [DEPLOYMENT.md](DEPLOYMENT.md)
- **Développement** : Guide [CONTRIBUTING.md](CONTRIBUTING.md)
- **Build PowerShell** : Guide [BUILD_POWERSHELL.md](BUILD_POWERSHELL.md)

---

**🎯 Objectif atteint ?** → [⭐ Donnez une étoile au projet !](https://github.com/kybaloo/chatbot)
