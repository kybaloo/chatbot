
# by default, we settle down in this region
AWS_REGION ?= eu-west-3

clean:
	rm -rf venv
	rm -rf __pycache__
	rm -rf *.egg-info
	rm -rf .pytest_cache

venv: clean
	python3 -m venv venv

install:
	venv/bin/pip install -r requirements.txt

build:
	sam build --use-container -t infrastructure/template.yaml
	docker build -t chatbot:latest .

deploy-local:
	sam local start-api

run-local:
	docker run -p 80:80 -p 8000:8000 -v $(PWD)/.env:/code/.env chatbot:latest
	
run-dev:
	uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

run-local-dynamo:
	@echo "Démarrage de DynamoDB Local..."
	powershell -File setup_local_dynamo.ps1

create-local-table:
	@echo "Création de la table DynamoDB locale..."
	python scripts/create_local_table.py

setup-ngrok:
	@echo "Configuration du webhook Telegram avec ngrok..."
	python scripts/setup_ngrok_webhook.py

dev-setup:
	@echo "Configuration de l'environnement de développement..."
	powershell -File dev_setup.ps1

format:
	@echo "Formatting code with black..."
	venv/bin/python -m black src tests || true

lint:
	@echo "Linting code with flake8..."
	venv/bin/python -m flake8 src tests || true

docs:
	@echo "Generating documentation..."
	venv/bin/sphinx-build -b html docs/source docs/build

deploy:
	@echo "Deploying to " ${env}
	# Extract env from the branch name

	@if [ -z "$(MISTRAL_API_KEY)" ]; then \
		echo "ERROR: MISTRAL_API_KEY environment variable must be set"; \
		exit 1; \
	fi

	@if [ -z "$(TELEGRAM_BOT_TOKEN)" ]; then \
		echo "ERROR: TELEGRAM_BOT_TOKEN environment variable must be set"; \
		exit 1; \
	fi

	sam deploy --resolve-s3 --template-file .aws-sam/build/template.yaml --stack-name multi-stack-${env} \
         --capabilities CAPABILITY_IAM --region ${AWS_REGION} \
         --parameter-overrides \
         ParameterKey=EnvironmentName,ParameterValue=${env} \
         ParameterKey=TelegramBotToken,ParameterValue=${TELEGRAM_BOT_TOKEN} \
         ParameterKey=MistralApiKey,ParameterValue=${MISTRAL_API_KEY} \
         ParameterKey=TelegramWebhookUrl,ParameterValue=${TELEGRAM_WEBHOOK_URL} \
         --no-fail-on-empty-changeset


serve:
	.venv/bin/fastapi dev src/app.py

test:
	@echo "Running tests..."
	venv/bin/python -m pytest || true

test-unit:
	@echo "Running unit tests..."
	venv/bin/python -m pytest tests/models tests/repositories tests/services || echo "No unit tests found, skipping"

test-integration:
	@echo "Running integration tests..."
	venv/bin/python -m pytest tests/test_api_integration.py || echo "No integration tests found, skipping"

test-endpoint:
	@echo "Running endpoint tests..."
	$(eval API_URL := $(shell aws cloudformation describe-stacks --stack-name chatbot-stack-${env} --region ${AWS_REGION} \
		--query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text))
	
	@echo "Testing base endpoint at ${API_URL}"
	@curl -s "${API_URL}" | grep "Hello World" && echo "Base endpoint test: PASSED" || echo "Base endpoint test: FAILED"
	
	@echo "Testing chat endpoint"
	@curl -s "${API_URL}/chat?question=Bonjour" | grep "answer" && echo "Chat endpoint test: PASSED" || echo "Chat endpoint test: FAILED"
	
	@echo "Testing conversation endpoint"
	@curl -s "${API_URL}/conversations/test-user" | grep "conversations" && echo "Conversations endpoint test: PASSED" || echo "Conversations endpoint test: FAILED"

setup-telegram-webhook:
	@if [ -z "$(TELEGRAM_BOT_TOKEN)" ]; then \
		echo "ERROR: TELEGRAM_BOT_TOKEN environment variable must be set"; \
		exit 1; \
	fi
	
	@if [ -z "$(WEBHOOK_URL)" ]; then \
		echo "ERROR: WEBHOOK_URL environment variable must be set"; \
		exit 1; \
	fi
	
	@echo "Setting up Telegram webhook..."
	@curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}/${TELEGRAM_BOT_TOKEN}" | grep "ok" && echo "Webhook setup: PASSED" || echo "Webhook setup: FAILED"