pipeline {
    agent any

    options {
        ansiColor('xterm')
    }

    environment {
        // Define environment variables here
        BOT_NAME = 'telegram-chatbot'
        AWS_REGION = 'eu-west-3' 
        TELEGRAM_BOT_TOKEN = credentials('telegram-bot-token')
        MISTRAL_API_KEY = credentials('mistral-api-key')
        WEBHOOK_URL = 'https://4y9lvphtwh.execute-api.eu-west-3.amazonaws.com/webhook/telegram'
        // AWS credentials sont gérés automatiquement par Jenkins
        DYNAMO_TABLE = "chatbot-conversations-kybaloo"
        LOG_LEVEL = "INFO"
        ENV_NAME = "kybaloo"
        ENABLE_TELEGRAM_BOT = "true"
        CONVERSATION_TTL_DAYS = "30"
    }

    stages {
        stage('Initialisation') {
            steps {
                sh "echo Branch name ${BRANCH_NAME}"
                sh "make venv && make install"
            }
        }
        
        stage('Environment variable injection'){
            steps {
                script{
                    try {
                        withCredentials([file(credentialsId: 'kybaloo-chatbot-env-file', variable: 'ENV_FILE')]) {
                            sh """
                                if [ -f "$ENV_FILE" ]; then
                                    echo "Injecting environment variables from credentials..."
                                    touch .env
                                    cat "$ENV_FILE" >> .env
                                else
                                    echo "Creating default .env file..."
                                    echo "ENV_NAME=${BRANCH_NAME}" > .env
                                    echo "AWS_REGION_NAME=${AWS_REGION}" >> .env
                                    echo "DYNAMO_TABLE=${DYNAMO_TABLE}" >> .env
                                    echo "MISTRAL_API_KEY=${MISTRAL_API_KEY}" >> .env
                                    echo "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}" >> .env
                                    echo "CONVERSATION_TTL_DAYS=${CONVERSATION_TTL_DAYS}" >> .env
                                fi
                            """
                        }
                    } catch (Exception e) {
                        echo "Warning during env file injection: ${e.message}"
                        sh """
                            echo "Creating default .env file..."
                            echo "ENV_NAME=${BRANCH_NAME}" > .env
                            echo "AWS_REGION_NAME=${AWS_REGION}" >> .env
                            echo "DYNAMO_TABLE=${DYNAMO_TABLE}" >> .env
                            echo "MISTRAL_API_KEY=${MISTRAL_API_KEY}" >> .env
                            echo "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}" >> .env
                            echo "CONVERSATION_TTL_DAYS=${CONVERSATION_TTL_DAYS}" >> .env
                        """
                    }
                }
            }
        }

        stage('Code Quality') {
            steps {
                script {
                    echo "Running code quality checks..."
                    sh "make format"
                }
            }
        }

        stage('Tests Unitaires') {
            steps {
                script {
                    echo "Running unit tests..."
                    sh "make test-unit"
                }
            }
        }
        
        stage('Tests Integration') {
            steps {
                script {
                    echo "Running integration tests..."
                    sh "make test-integration"
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    // Add your build commands here
                    echo "Building the project..."
                    sh "make build"
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "Deploying the project..."
                    
                    // Configuration de l'environnement AWS
                    withCredentials([
                        string(credentialsId: 'telegram-bot-token', variable: 'TELEGRAM_BOT_TOKEN'),
                        string(credentialsId: 'mistral-api-key', variable: 'MISTRAL_API_KEY')
                    ]) {
                        
                        // Déploiement via CloudFormation
                        sh """
                            aws cloudformation deploy \\
                                --template-file infrastructure/template.yaml \\
                                --stack-name chatbot-stack-${BRANCH_NAME} \\
                                --region ${AWS_REGION} \\
                                --parameter-overrides \\
                                    EnvironmentName=${BRANCH_NAME} \\
                                    MistralApiKey=${MISTRAL_API_KEY} \\
                                    TelegramBotToken=${TELEGRAM_BOT_TOKEN} \\
                                    WebhookUrl=${WEBHOOK_URL} \\
                                    LogLevel=${LOG_LEVEL} \\
                                    EnableTelegramBot=${ENABLE_TELEGRAM_BOT} \\
                                    ConversationTTLDays=${CONVERSATION_TTL_DAYS} \\
                                --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
                        """                        // Récupérer l'URL de l'API déployée
                        sh """
                            API_URL=\$(aws cloudformation describe-stacks \\
                                --stack-name chatbot-stack-${BRANCH_NAME} \\
                                --region ${AWS_REGION} \\
                                --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \\
                                --output text)
                            echo "API déployée à: \${API_URL}"
                            
                            # Mettre à jour l'environnement avec l'URL obtenue
                            export WEBHOOK_URL="\${API_URL}/webhook/telegram"
                            echo "WEBHOOK_URL=\${WEBHOOK_URL}"
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "Fin de l'exécution du pipeline"
            // Ne pas utiliser cleanWs() qui nécessite un contexte spécifique
        }
        success {
            echo "Build réussi ! L'URL du webhook est : ${WEBHOOK_URL}"
        }
        failure {
            echo "Échec du build ! Consultez les logs pour plus d'informations."
        }
    }
}
