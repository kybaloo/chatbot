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
        WEBHOOK_URL = ''
        AWS_CREDENTIALS = credentials('aws-credentials')
        DYNAMO_TABLE = "chatbot-conversations-${BRANCH_NAME}"
        LOG_LEVEL = "INFO"
        ENV_NAME = "${BRANCH_NAME}"
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
                    withCredentials([file(credentialsId: 'kybaloo-chatbot-env-file', variable: 'ENV_FILE')]) {
                        sh "cat $ENV_FILE >> .env"
                    }
                }
            }
        }


        stage('Code Quality') {
            steps {
                script {
                    echo "Running code quality checks..."
                    sh "make lint"
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
                    withAWS(credentials: 'aws-credentials', region: "${AWS_REGION}") {
                        
                        // Définir la valeur du webhook URL selon l'environnement
                        if (BRANCH_NAME == 'prod') {
                            WEBHOOK_URL = "https://api.votre-domaine.com" // Remplacez par votre URL de production
                        } else if (BRANCH_NAME == 'preprod') {
                            WEBHOOK_URL = "https://preprod.votre-domaine.com" // Remplacez par votre URL de préproduction
                        } else if (BRANCH_NAME == 'kybaloo') {
                            // Pour un premier déploiement, l'URL sera vide puis sera mise à jour après obtention de l'URL API Gateway
                            // Le bot fonctionnera en mode polling jusqu'à ce que le webhook soit configuré
                            echo "Déploiement initial sur l'environnement kybaloo sans webhook configuré"
                            // Le webhook sera automatiquement configuré dans l'étape 'Configure Webhook' après déploiement
                        }
                        
                        // Déploiement via CloudFormation
                        sh """
                            aws cloudformation deploy \\
                                --template-file infrastructure/template.yaml \\
                                --stack-name chatbot-stack-${BRANCH_NAME} \\
                                --parameter-overrides \\
                                    EnvironmentName=${BRANCH_NAME} \\
                                    MistralApiKey=${MISTRAL_API_KEY} \\
                                    TelegramBotToken=${TELEGRAM_BOT_TOKEN} \\
                                    WebhookUrl=${WEBHOOK_URL} \\
                                    LogLevel=${LOG_LEVEL} \\
                                    EnableTelegramBot=${ENABLE_TELEGRAM_BOT} \\
                                    ConversationTTLDays=${CONVERSATION_TTL_DAYS} \\
                                --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
                        """
                        
                        // Récupérer l'URL de l'API déployée
                        sh """
                            API_URL=\$(aws cloudformation describe-stacks \\
                                --stack-name chatbot-stack-${BRANCH_NAME} \\
                                --query 'Stacks[0].Outputs[?OutputKey==\`ApiUrl\`].OutputValue' \\
                                --output text)
                            echo "API déployée à: \${API_URL}"
                        """
                    }
                }
            }
        }

        stage('Configure Webhook') {
            steps {
                script {
                    echo "Configuring Telegram webhook..."
                    
                    withAWS(credentials: 'aws-credentials', region: "${AWS_REGION}") {
                        // Récupérer l'URL de l'API déployée
                        sh """
                            API_URL=\$(aws cloudformation describe-stacks \\
                                --stack-name chatbot-stack-${BRANCH_NAME} \\
                                --query 'Stacks[0].Outputs[?OutputKey==\`ApiUrl\`].OutputValue' \\
                                --output text)
                            
                            # Configurer le webhook Telegram avec l'URL de l'API et le chemin /webhook/telegram
                            if [ -n "\${API_URL}" ]; then
                                FULL_WEBHOOK_URL="\${API_URL}/webhook/telegram"
                                echo "Setting webhook to: \${FULL_WEBHOOK_URL}"
                                
                                # Appeler l'API Telegram pour configurer le webhook
                                curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \\
                                    -H "Content-Type: application/json" \\
                                    -d \"{\\"url\\":\\"\${FULL_WEBHOOK_URL}\\", \\"drop_pending_updates\\":true}\"
                                
                                # Vérifier si le webhook a été correctement configuré
                                curl -X GET "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
                            else
                                echo "Failed to get API URL, webhook not configured"
                            fi
                        """
                    }
                }
            }
        }
        
        stage('Test endpoint'){
            steps {
                script {
                    echo "Testing the endpoint..."
                    
                    withAWS(credentials: 'aws-credentials', region: "${AWS_REGION}") {
                        // Récupérer l'URL de l'API déployée
                        sh """
                            API_URL=\$(aws cloudformation describe-stacks \\
                                --stack-name chatbot-stack-${BRANCH_NAME} \\
                                --query 'Stacks[0].Outputs[?OutputKey==\`ApiUrl\`].OutputValue' \\
                                --output text)
                            
                            # Test de l'endpoint racine
                            echo "Test de l'API à \${API_URL}"
                            curl -s \${API_URL} | grep "ChatBot API"
                            
                            # Test de l'endpoint pour créer une conversation
                            echo "Test de création de conversation"
                            RESPONSE=\$(curl -s -X POST "\${API_URL}/conversations" \
                                -H "Content-Type: application/json" \
                                -d '{"user_id":"test-user","title":"Test Conversation","model_id":"mistral-medium"}')
                            echo "\${RESPONSE}" | grep "conversation_id"
                            
                            # Test de l'endpoint pour ajouter un message et obtenir une réponse
                            echo "Test d'ajout de message"
                            CONVO_ID=\$(echo "\${RESPONSE}" | grep -o '"conversation_id":"[^"]*"' | cut -d '"' -f 4)
                            RESPONSE=\$(curl -s -X POST "\${API_URL}/conversations/test-user/\${CONVO_ID}/messages" \
                                -H "Content-Type: application/json" \
                                -d '{"content":"Bonjour, comment ça va?"}')
                            echo "\${RESPONSE}" | grep "ai_response"
                            
                            # Si on est en prod ou preprod, configurer le webhook Telegram
                            if [[ "${BRANCH_NAME}" == "prod" || "${BRANCH_NAME}" == "preprod" ]]; then
                                EC2_PUBLIC_IP=\$(aws cloudformation describe-stacks \\
                                    --stack-name chatbot-stack-${BRANCH_NAME} \\
                                    --query 'Stacks[0].Outputs[?OutputKey==\`EC2PublicIP\`].OutputValue' \\
                                    --output text)
                                    
                                echo "Configuration du webhook Telegram sur l'instance EC2 \${EC2_PUBLIC_IP}"
                                # Configuration du webhook avec le nouveau chemin webhook/telegram
                                curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}/webhook/telegram"
                            fi
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                // Clean up and generate reports
                echo "Generating test reports..."
                
                // Archive test results if they exist
                if (fileExists('test-results')) {
                    archiveArtifacts artifacts: 'test-results/**/*', allowEmptyArchive: true
                }
                
                // Clean up resources if needed
                echo "Cleaning up resources..."
            }
        }
        success {
            script {
                // Notify success
                echo "Build succeeded!"
                // Envoyer une notification dans un groupe Telegram dédié au CI/CD
                sh """
                    # Récupérer l'URL de l'API
                    API_URL=\$(aws cloudformation describe-stacks \
                        --stack-name chatbot-stack-${BRANCH_NAME} \
                        --region ${AWS_REGION} \
                        --query 'Stacks[0].Outputs[?OutputKey==\`ApiUrl\`].OutputValue' \
                        --output text)
                        
                    # Envoyer la notification avec l'URL
                    curl -X POST https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage \
                        -d chat_id=<CHAT_ID_CI> \
                        -d parse_mode=Markdown \
                        -d text='✅ *Déploiement réussi* pour la branche `${BRANCH_NAME}` du chatbot !\n\nAPI: '\${API_URL}'
                """
            }
        }
        failure {
            script {
                // Notify failure
                echo "Build failed!"
                // Envoyer une notification dans un groupe Telegram dédié au CI/CD
                sh """
                    # Envoyer la notification avec le lien vers les logs
                    BUILD_URL=${BUILD_URL}
                    curl -X POST https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage \
                        -d chat_id=<CHAT_ID_CI> \
                        -d parse_mode=Markdown \
                        -d text='❌ *Échec du déploiement* pour la branche `${BRANCH_NAME}` du chatbot.\n\n[Voir les logs](\${BUILD_URL}console)'
                """
            }
        }
    }

}