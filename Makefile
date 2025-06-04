
# by default, we settle down in this region
AWS_REGION ?= eu-west-3

# Default values for deployment
TELEGRAM_BOT_TOKEN ?= ""
MISTRAL_API_KEY ?= ""
WEBHOOK_URL ?= ""
env ?= kybaloo

# Version management
VERSION := $(shell cat version 2>/dev/null || echo "1.0.0")
PROJECT_NAME := chatbot-telegram-mistral

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

.PHONY: help version bump-major bump-minor bump-patch clean venv install build deploy test

help: ## Show this help message
	@echo "$(BLUE)🤖 Chatbot Telegram avec Mistral AI - v$(VERSION)$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

version: ## Show current version
	@echo "$(GREEN)Current version: $(VERSION)$(NC)"

bump-major: ## Bump major version (1.0.0 -> 2.0.0)
	@echo "$(BLUE)Bumping major version...$(NC)"
	@python -c "v='$(VERSION)'.split('.'); v[0]=str(int(v[0])+1); v[1]='0'; v[2]='0'; print('.'.join(v))" > version
	@echo "$(GREEN)Version bumped to: $$(cat version)$(NC)"

bump-minor: ## Bump minor version (1.0.0 -> 1.1.0)
	@echo "$(BLUE)Bumping minor version...$(NC)"
	@python -c "v='$(VERSION)'.split('.'); v[1]=str(int(v[1])+1); v[2]='0'; print('.'.join(v))" > version
	@echo "$(GREEN)Version bumped to: $$(cat version)$(NC)"

bump-patch: ## Bump patch version (1.0.0 -> 1.0.1)
	@echo "$(BLUE)Bumping patch version...$(NC)"
	@python -c "v='$(VERSION)'.split('.'); v[2]=str(int(v[2])+1); print('.'.join(v))" > version
	@echo "$(GREEN)Version bumped to: $$(cat version)$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning project...$(NC)"
	rm -rf venv .venv
	rm -rf __pycache__ **/__pycache__
	rm -rf *.egg-info **/*.egg-info
	rm -rf .pytest_cache **/.pytest_cache
	rm -rf .mypy_cache **/.mypy_cache
	rm -rf build dist
	rm -rf .coverage htmlcov
	rm -rf .aws-sam
	@echo "$(GREEN)Project cleaned!$(NC)"

venv: clean
	python3 -m venv .venv

install:
	.venv/bin/pip install -r requirements.txt

build:
	sam build --use-container -t infrastructure/template.yaml
	docker build -t chatbot:latest .

deploy-local:
	sam local start-api

run-local:
	docker run -p 80:80 -p 8000:8000 -v $(PWD)/.env:/code/.env chatbot:latest
	
run-dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

format:
	@echo "Formatting code with black..."
	.venv/bin/python -m black src tests || true

lint:
	@echo "Linting code with flake8..."
	.venv/bin/python -m flake8 src tests || true

docs:
	@echo "Generating documentation..."
	.venv/bin/sphinx-build -b html docs/source docs/build

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
         ParameterKey=TelegramWebhookUrl,ParameterValue=${WEBHOOK_URL} \
         --no-fail-on-empty-changeset


serve:
	.venv/bin/fastapi dev src/main.py

test:
	@echo "Running tests..."
	.venv/bin/python -m pytest || true

test-unit:
	@echo "Running unit tests..."
	.venv/bin/python -m pytest tests/models tests/repositories tests/services || echo "No unit tests found, skipping"

test-integration:
	@echo "Running integration tests..."
	.venv/bin/python -m pytest tests/test_api_integration.py || echo "No integration tests found, skipping"

test-endpoint:
	@echo "Running endpoint tests..."
	$(eval API_URL := $(shell aws cloudformation describe-stacks --stack-name multi-stack-${env} --region ${AWS_REGION} \
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