pipeline {
    agent any

    environment {
        AWS_REGION   = "us-east-1"
        AWS_ACCOUNT  = "024697548457"
        APP_NAME     = "organizeit"
        IMAGE_TAG    = "latest"
        ECR_REGISTRY = "${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_REPO     = "${ECR_REGISTRY}/${APP_NAME}"
        ECS_CLUSTER  = "organizeit"           // <-- replace with your ECS cluster name
        ECS_SERVICE  = "organizeit-ultimate-service-c09qmchl"       // <-- replace with your ECS service name
        TASK_FAMILY  = "organizeit-ultimate"          // <-- replace with your ECS task definition family
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/deepakkr57118/OrganizeIt.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${APP_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Login to ECR') {
            steps {
                script {
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    """
                }
            }
        }

        stage('Create ECR Repository if Not Exists') {
            steps {
                script {
                    sh """
                        aws ecr describe-repositories --repository-names ${APP_NAME} --region ${AWS_REGION} || \
                        aws ecr create-repository --repository-name ${APP_NAME} --region ${AWS_REGION}
                    """
                }
            }
        }

        stage('Tag & Push Image') {
            steps {
                script {
                    sh """
                        docker tag ${APP_NAME}:${IMAGE_TAG} ${ECR_REPO}:${IMAGE_TAG}
                        docker push ${ECR_REPO}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Register New Task Definition') {
            steps {
                script {
                    // fetch the existing task def and update container image
                    sh """
                        aws ecs describe-task-definition \
                            --task-definition ${TASK_FAMILY} \
                            --region ${AWS_REGION} \
                            --query taskDefinition > taskdef.json
                        
                        cat taskdef.json | \
                        jq '.containerDefinitions[0].image = "${ECR_REPO}:${IMAGE_TAG}"' | \
                        jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)' \
                        > new-taskdef.json
                        
                        aws ecs register-task-definition \
                            --region ${AWS_REGION} \
                            --cli-input-json file://new-taskdef.json
                    """
                }
            }
        }

        stage('Deploy to ECS') {
            steps {
                script {
                    sh """
                        aws ecs update-service \
                            --cluster ${ECS_CLUSTER} \
                            --service ${ECS_SERVICE} \
                            --force-new-deployment \
                            --region ${AWS_REGION}
                    """
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout ${ECR_REGISTRY}'
        }
    }
}
