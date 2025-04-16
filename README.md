# DEPI DevOps Graduation Project : Simplifying and Dockerizing an NLP Application with DevOps tools

This project is a Flask web application that enables users to register, log in, and perform sentiment analysis on an article URL using the Hugging Face Inference API. The application is built with a focus on simplifying and full automating the complete deployment process using modern DevOps tools and practices.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [CI/CD Pipeline](#ci-cd-pipeline)
- [Tools and Technologies](#tools-and-technologies)
- [Installation and Usage](#installation-and-usage)
- [Contributing](#contributing)
- [Contact](#contact)

---

## Overview

This project demonstrates how to build a containerized NLP (Natural Language Processing) application with end-to-end automation of the deployment process. The application allows users to:

- **Sign Up & Log In:** Users register and authenticate via a PostgreSQL database.
- **Sentiment Analysis:** After logging in, users enter an article URL, and the application calls the Hugging Face Inference API to analyze the sentiment of the article.
- **Display Results:** The sentiment analysis results are displayed back to the user.

The goal is to simplify the deployment process and to dockerize the NLP application using a variety of DevOps tools and best practices.

---

## Features

- **User Authentication:**  
  - Registration and login functionality using a PostgreSQL database.
  
- **Sentiment Analysis:**  
  - A single-page interface for users to input an article URL.
  - Integration with the Hugging Face Inference API to perform sentiment analysis.
  
- **Containerization:**  
  - The application is split into two main Docker containers:
    - Flask application container.
    - PostgreSQL database container.

- **Containers Orchestration using Kubernetes:**  
  - the applicaion is deployed locally through minikube cluster containing:
    - PostgreSQL deployment and with ClusterIP service.
    - Flask APP deployment with LoadBalancer service
    - Secret containing DOCKERHUB_USERNAME and DOCKERHUB_PASSWORD to pull the created image of the application
    - Secret containg application environment variables and credentials for applicaion and PostgreSQL 
    
- **CI/CD Pipeline using Jenkins:**  
  - Full automate building, testing, and deployment through Jenkins.
  - Docker image building and publishing to Docker Hub.
  - Deployment automation using Ansible, Kubernetes, and AWS CloudFormation.

- **IAC using AWS cloudformation:**  
  - Provision AWS infrastructure using AWS CloudFormation (VPC, public network, Internet Gateway, routing table, EC2, security groups).


---

## Architecture

The application follows a multi-container architecture with the following components:

- **Flask Application Container:**  
  - Hosts the web application responsible for user management and sentiment analysis.
  
- **PostgreSQL Container:**  
  - Manages user data and credentials.

- **CI/CD Pipeline Stages:**  
  1. **Environment Setup:**  
     - Use a `.env` file to store environment variables (API keys, database credentials, Docker Hub and AWS credentials).
  2. **Build Stage:**  
     - Dockerize the Flask app using a `Dockerfile` and build its image.
  3. **Test Stage:**  
     - Run containers for both PostgreSQL and Flask applications using Docker Compose, and execute test cases with Pytest.
  4. **Push Stage:**  
     - Tag and push the Flask app's Docker image to Docker Hub.
  5. **Local Deployment:**  
     - Deploy the project locally using Ansible and Kubernetes:
       - Create secrets from the `.env` file.
       - Deploy the Flask app (with load balancer service) and PostgreSQL (with ClusterIP service).
  6. **AWS Infrastructure:**  
     - Provision AWS infrastructure using AWS CloudFormation (VPC, public network, Internet Gateway, routing table, EC2, security groups).
  7. **Remote Deployment on AWS:**  
     - Use Ansible to deploy the project to an AWS EC2 instance running the Docker containers using Docker Compose.

---

## CI/CD Pipeline

The pipeline is configured in Jenkins and includes the following stages:

1. **Set Environment Variables:**
   - Read API keys, database credentials, and other secrets from a `.env` file.
   
2. **Build Stage:**
   - Dockerize the Flask app using a `Dockerfile`.
   - Build the Docker image for the Flask application.
   
3. **Test Stage:**
   - Run Docker Compose to start the PostgreSQL container and the Flask app container.
   - Override the Flask app’s main command with `pytest` to run automated tests.
   
4. **Push Stage:**
   - Tag the Docker image with the pipeline number.
   - Push the image to Docker Hub.
   
5. **Local Deployment:**
   - Use an Ansible playbook with a localhost inventory to:
     - Create Kubernetes secrets for the app and Docker Hub registry.
     - Deploy the Flask app (pulling the latest Docker image from Docker Hub and exposing it via a LoadBalancer).
     - Deploy the PostgreSQL container (using a ClusterIP service).
     
6. **AWS Infrastructure & Remote Deployment:**
   - Deploy AWS infrastructure using CloudFormation to set up networking, compute, and security (VPC, Internet Gateway, Routing Table, EC2, Security Group).
   - Use Ansible (with an inventory file containing the EC2 instance IP) to deploy the project remotely on AWS, running the two Docker containers via Docker Compose.

---

## Tools and Technologies

- **Programming & Frameworks:**  
  - Python, Flask
- **Database:**  
  - PostgreSQL
- **testing tools:**
   - Pytest
- **Containerization:**  
  - Docker, Docker Compose
- **CI/CD:**  
  - Jenkins
- **Configuration Management & Orchestration:**  
  - Ansible, Kubernetes
- **Cloud Infrastructure:**  
  - AWS CloudFormation, Terraform
- **API Integration:**  
  - Hugging Face Inference API for NLP sentiment analysis

---

## Installation and Usage

### Prerequisites

- Docker and Docker Compose installed
- Python 3.x installed
- PostgreSQL server (or we already use Docker container)
- Jenkins for CI/CD pipeline
- Ansible installed for deployment automation
- AWS CLI (if deploying to AWS)
- minikube for locally created containers Orchestration 

### Local Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ahosny333/dockerize_nlp_app.git
   cd dockerize_nlp_app
   ```

2. **Set up Environment Variables:**
Create a .env file in the project root with the following variables:

   ```
   FLASK_APP=app
   API_KEY=your_huggingface_api_key
   DATABASE_URL=postgresql://username:password@localhost/dbname
   DOCKERHUB_USERNAME=your_dockerhub_username
   DOCKERHUB_PASSWORD=your_dockerhub_password
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   ```

3. **Set up the AWS CLI with AWS account credentials:**

   ```bash
   aws configure 
   # set the AWS Access key ID,Secret access key
   ```

3. **Start Minikube cluster:**

   ```bash
   minikube start
   ```

4. **Run the CI/CD pipeline in Jenkins**:
After complete successful run for pipeline in jenkins the application will be deployed locally at host machine and remotely on remote AWS EC2
   - Access the application locally

      ```
      http://localhost:5000
      ```
   
   - Access the application through AWS EC2 instance

      ```
      http://AWS-instance-IP:5000
      ```
   
---
## Contributing

#### Contributions are welcome! Please follow these steps:

1. Fork the repository.

2. Create a new branch (git checkout -b feature-branch).

3. Make your changes.

4. Commit your changes (git commit -m 'Add new feature').

5. Push to the branch (git push origin feature-branch).

6. Open a pull request.

---

## Contact
For questions or comments, please reach out to me at [my email](hj.ahmed.hosny@gmail.com) or check my [portfolio](https://ahosny333.github.io/portfolio/) for more projects.



