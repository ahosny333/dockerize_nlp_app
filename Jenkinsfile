pipeline {
  agent any

  environment {
    // Reference Jenkins credentials stored with ID "dockerhub-credentials-id"
    DOCKERHUB_CREDENTIALS = credentials('dockerhub')
    MY_IMAGE_NAME = credentials('IMAGE_NAME_ID')
    BUILD_TAG = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Prepare Environment') {
      steps {
        withCredentials([file(credentialsId: 'my_env_id', variable: 'ENV_FILE')]) {
          sh 'cp $ENV_FILE .env'
        }
      }
    }
    
    stage('Build Docker Image') {
      steps {
        
        sh 'docker compose build'
        
        // Option 2: If you have a dedicated Dockerfile for the Flask app:
        // sh "docker build -t ${MY_IMAGE_NAME}:${BUILD_TAG} ."
      }
    }
    
    stage('Test') {
      steps {
        // Spin up the test environment
        // sh 'docker-compose up -d'
        // up database for test
        sh 'docker compose up -d db'
        sh 'sleep 20'
        // Run tests in the appropriate container (assuming it's named "web")
        sh 'docker compose run --rm flask_app pytest'
        // Tear down the test environment
        sh 'docker compose down'
      }
    }
    
    stage('Push to Docker Hub') {
      steps {
        script {
          // Log in to Docker Hub using Jenkins credentials
          sh "docker login -u ${DOCKERHUB_CREDENTIALS_USR} -p ${DOCKERHUB_CREDENTIALS_PSW}"
          // Tag the image for latest and build-specific version
          // sh "docker tag ${MY_IMAGE_NAME}:${BUILD_TAG} ${MY_IMAGE_NAME}:latest"
          // Push both tags
          // sh "docker push ${MY_IMAGE_NAME}:latest"
          sh "docker push ${MY_IMAGE_NAME}:${BUILD_TAG}"
        }
      }
    }
    
    stage('Deploy') {
      steps {
        // Deploy using a production Docker Compose file
        sh 'docker compose up -d'
        // Alternatively, you could invoke deployment scripts or orchestrate deployments via other tools
      }
    }
  }
  
  post {
   always {
      sh 'docker compose down'
      sh 'rm -f .env'
      
    }
    success {
      echo 'Pipeline completed successfully!'
      // Add notification steps (e.g., send Slack or email notifications)
    }
    failure {
      echo 'Pipeline failed!'
      // Optionally notify stakeholders of failure
    }
  }
}
