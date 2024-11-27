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
