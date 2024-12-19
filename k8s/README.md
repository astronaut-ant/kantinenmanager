# How to setup prod?

## Setup Kubernetes

-> [MicroK8s](https://microk8s.io/#install-microk8s)

```bash
sudo snap install microk8s --classic # Install on Linux

microk8s status --wait-ready # Check status while K8s starts

microk8s enable dashboard # Enable dashboard addon

sudo snap install kubectl --classic # Install kubectl client

sudo snap install helm --classic # Install helm
```

## Setup application

1. Connect GitLab to the Kubernetes Cluster (-> via GitLab integration)

2. Generate an Access Token for DockerHub and create a K8s secret for authentication:

```bash
kubectl create secret docker-registry regcred docker-server=DOCKER_REGISTRY_SERVER --docker-username=DOCKER_USER --docker-password=DOCKER_PASSWORD
```

3. Create the following generic secrets for the application. The values may be random and must not contain special characters.

```bash
kubectl create secret generic dbpassword --from-literal=DB_PASSWORD=supersecret

kubectl create secret generic jwtsecret --from-literal=JWT_SECRET=supersecret

kubectl create secret generic initialadmin --from-literal=INITIAL_ADMIN_PASSWORD=supersecret
```

4. Generate a new self-signed ssl certificate

```bash
mkdir /home/swtp/certs
cd /home/swtp/certs

# create a new cert without a password
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes 
# Country Name: DE
# State: Saxony
# Locality: Leipzig
# Organization Name: SEP Gruppe 16
# Organizational Unit Name: 
# Common Name: <ip of server>

# create K8s secret
kubectl create secret tls self-signed-tls --cert=./cert.pem --key=./key.pem
```

5. Now run the pipeline. Et voilà ✌️

## Access Dashboard

```bash
microk8s dashboard-proxy
```

## Use `kubectl` on local machine

Run the following command in the VM. It will print the config to stdout. Copy everything from the output.

```bash
microk8s config
```

On your local machine, create the following directory and file: `~/.kube/config` and paste the config in this file.

Then, install `kubectl` on your local machine ([see](https://kubernetes.io/docs/tasks/tools/#kubectl)).

Test: `kubectl cluster-info`

## Helpful commands

```bash
kubectl cluster-info # Get cluster information

kubectl get all # Get all resources

kubectl get pods # Get pods

kubectl describe pod <pod-name> # Describe a specific pod

kubectl apply -f <file.yaml> # Apply a configuration file

kubectl delete -f <file.yaml> # Delete resources from a file

kubectl exec -it <pod-name> -- <command> # Execute a command in a container

kubectl scale deployment <deployment-name> --replicas=<number> # Scale a deployment

kubectl rollout status deployment <deployment-name> # Get status of deployment
```

## Create an user in Postgres

```bash
kubectl get pods

kubectl exec -it <db-deployment-...> -- /bin/bash

psql -U postgres

CREATE USER adminer WITH ENCRYPTED PASSWORD '<password>';

GRANT ALL ON SCHEMA public TO adminer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO adminer;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO adminer;

# For future additions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO adminer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO adminer;
```