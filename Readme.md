# Ansible playbook to deploy a Flask app and PostgreSQL on Minikube.

## Introduction
This playbook deploys a `Flask` app and `PostgreSQL` on `Minikube`. The `Flask` app is a simple `NLP` app that tokenizes a given text. The app is deployed as a `Kubernetes Deployment` and exposed as a `Kubernetes Service`. The `PostgreSQL` database is also deployed as a `Kubernetes Deployment` and exposed as a `Kubernetes Service`.

## Prerequisites
- Minikube
- Ansible

## Ansible to use Minikube
Ensure Minikube's context is active in `~/.kube/config` for Ansible to target the Minikube cluster.

### **Step 1: Start Minikube**
```bash
minikube start
```

#### 2. Verify Minikube is the current context:
```bash
yasser@kane:~/dockerize_nlp_app$ minikube kubectl -- config current-context
minikube

yasser@kane:~/dockerize_nlp_app$ cat ~/.kube/config
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /home/yasser/.minikube/ca.crt
[...omit for brevity...]
current-context: minikube
kind: Config
preferences: {}
users:
- name: minikube
[...omit for brevity...]
```

#### **Check Available Contexts**:
   ```bash
   yasser@kane:~/dockerize_nlp_app$ minikube kubectl --  config get-contexts
   CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
   *         minikube   minikube   minikube   default
   ```
#### **Switch Context**: (Optional - If not already set - in my case it is already set becuase I downloaded the minikube only)
   ```bash
   minikube kubectl -- config use-context minikube
```

---

## Directory Structure
```
ansible-flask-postgres/
│
├── roles/
│   ├── postgres/
│   │   ├── tasks/
│   │   │   └── main.yml     # Tasks for PostgreSQL deployment
│   │   └── files/
│   │       ├── postgres-deployment.yml   # PostgreSQL Deployment
│   │       └── postgres-service.yml      # PostgreSQL Service
│   └── flask_app/
│       ├── tasks/
│       │   └── main.yml     # Tasks for Flask app deployment
│       └── files/
│           ├── flask-deployment.yml      # Flask Deployment
│           └── flask-service.yml         # Flask Service
└── main_playbook.yml                 # Main playbook file
```

### File Descriptions

#### `main_playbook.yml`
This is the main Ansible playbook that orchestrates the deployment of both the Flask app and PostgreSQL. It ensures Minikube is running, creates Kubernetes secrets, and invokes the roles for PostgreSQL and Flask app deployment.

#### `roles/postgres/tasks/main.yml`
This file contains the tasks to deploy the PostgreSQL database. It creates the PostgreSQL Deployment and Service using the Kubernetes manifests defined in the `files` directory.

#### `roles/postgres/files/postgres-deployment.yml`
Defines the Kubernetes Deployment for PostgreSQL, specifying the container image, environment variables, and resource limits.

#### `roles/postgres/files/postgres-service.yml`
Defines the Kubernetes Service for PostgreSQL, exposing it internally within the cluster.

#### `roles/flask_app/tasks/main.yml`
This file contains the tasks to deploy the Flask app. It creates the Flask Deployment and Service using the Kubernetes manifests defined in the `files` directory.

#### `roles/flask_app/files/flask-deployment.yml`
Defines the Kubernetes Deployment for the Flask app, specifying the container image, environment variables, and resource limits.

#### `roles/flask_app/files/flask-service.yml`
Defines the Kubernetes Service for the Flask app, exposing it on a NodePort for external access.

---

## To use this playbook:

1. Install required collections:
```bash
yasser@kane:~/dockerize_nlp_app$ ansible-galaxy collection install community.general
Starting galaxy collection install process
Nothing to do. All requested collections are already installed. If you want to reinstall them, consider using `--force`.
```

To load the environment variables from the `.env` file, install the `community.general` collection. The `community.general` collection provides the `community.general.envfile` module, which allows you to load environment variables from a file. At the main_playbook.yml file, the `community.general` collection is used to load the environment variables from the `.env` file. The `community.general` collection

Should be already installed by default.

2. Load the Docker image into Minikube: (Required in the pipeline)

```bash
minikube image load my-flask-app:latest
```

3. Run the playbook:
```bash
ansible-playbook main_playbook.yml -e "FLASK_IMAGE=my-flask-app:latest"
```

---

## Conclusion
This Ansible playbook automates the deployment of a Flask app and PostgreSQL on Minikube. It demonstrates how to use Ansible to manage Kubernetes resources and deploy applications in a Kubernetes cluster. The playbook can be extended to include additional services, configurations, and customizations as needed.