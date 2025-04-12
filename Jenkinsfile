pipeline {
  agent any

  environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub')
    MY_IMAGE_NAME = credentials('IMAGE_NAME_ID')
    BUILD_TAG = "${env.BUILD_NUMBER}"
    AWS_DEFAULT_REGION = 'us-east-1'
    aws_EnvironmentName = 'nlp-app'
    aws_project = 'nlp_project'
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
        // sh "docker build -t ${MY_IMAGE_NAME}:${BUILD_TAG} ."
      }
    }
    
    stage('Test') {
      steps {
        sh 'docker compose up -d db'
        sh 'sleep 20'
        // Run tests in the appropriate container 
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
          sh "docker push ${MY_IMAGE_NAME}:${BUILD_TAG}"
        }
      }
    }

    stage('deploy using kubeneates') {
      steps {
        script {
            sh '''
            chmod u+w .env 
            echo "BUILD_TAG=${BUILD_TAG}" >> .env
            echo "docker_user=${DOCKERHUB_CREDENTIALS_USR}" >> .env
            minikube start
            alias k="minikube kubectl --"
            k create secret generic my-secret --from-env-file=.env
            k apply -f kubernates/db-deployment.yml
            k create secret docker-registry my-dockerhub-secret \
            --docker-username=${DOCKERHUB_CREDENTIALS_USR} \
            --docker-password=${DOCKERHUB_CREDENTIALS_PSW} \
            --docker-email=hj.ahmed.hosny@gmail.com
            set -a
            source .env
            set +a
            envsubst < kubernates/deployment-template.yaml > kubernates/deployment.yaml
            k apply -f kubernates/deployment.yaml

            '''
          
        }
      }
    }
    
    // stage('Deploy') {
    //   steps {
    //     // Deploy using a production Docker Compose file
    //     sh 'docker compose up -d'
    //   }
    // }

    stage('build aws infrastructure'){
      steps{
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'myaws',
                                  accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                                  secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                    // Deploy or update CloudFormation stack using AWS CLI
                    sh """
                      aws cloudformation deploy --template-file aws_infrastructure/network.yml --stack-name "nlp-network" \
                        --parameter-overrides EnvironmentName=${aws_EnvironmentName} WorkflowID="12345678" \
                        --tags project=${aws_project}

                      aws cloudformation deploy --template-file aws_infrastructure/servers.yml --stack-name "nlp-server" \
                        --parameter-overrides EnvironmentName=${aws_EnvironmentName} id="12345678" \
                         --tags project=${aws_project}
                         
                    aws cloudformation list-exports --query "Exports[?Name==\\`WorkflowID\\`].Value" --no-paginate --output text
                    """

                    
        }
      }
    }
    
    stage('Configure EC2 with Ansible') {
      steps {
        // Use Jenkins credentials for your SSH key
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'myaws',
                                  accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                                  secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'],sshUserPrivateKey(credentialsId: 'ec2_ssh', keyFileVariable: 'SSH_KEY')]) {
          // Create the inventory file using a shell script without needing extra Groovy code
          sh '''
            INSTANCE_IP=$(aws ec2 describe-instances \
              --query "Reservations[*].Instances[*].PublicIpAddress" \
              --filters "Name=tag:Name,Values=elgris-12345678" \
              --output text)
            # Optionally add remote host key to known_hosts
            ssh-keyscan -H ${INSTANCE_IP} >> ~/.ssh/known_hosts
            echo "[ec2]" > inventory
            echo "${INSTANCE_IP} ansible_user=ubuntu" >> inventory
            cat inventory
          '''
          // update .env file including all required parameters 
          sh '''
            chmod u+w .env 
            echo "BUILD_TAG=${BUILD_TAG}" >> .env
            tar -czvf project.tar.gz migrations templates Dockerfile app.py docker-compose.yml extensions.py models.py requirements.txt .env
            
          '''
          // Run the Ansible playbook using the generated inventory file and the SSH key
          sh "ansible-playbook -i inventory ansible/playbook.yml --private-key ${SSH_KEY}"

          // OR Run the Ansible playbook, disabling strict host key checking -- not used as i used add remote host key to known_hosts
          // sh "ansible-playbook -i inventory ansible/playbook.yml --private-key ${SSH_KEY} --ssh-extra-args '-o StrictHostKeyChecking=no'"
           
        }
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

