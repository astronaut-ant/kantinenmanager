# Setup Grapfana, Prometheus and Loki

https://grafana.com/docs/loki/latest/visualize/grafana/#grafana-explore

## create namespace in K8s

```bash
microk8s enable hostpath-storage
kubectl create namespace monitoring
```

## kube-prometheus-stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prom-stack prometheus-community/kube-prometheus-stack -f helm/prom-values.yml -n monitoring
```

## Loki

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade --install loki grafana/loki-stack -n monitoring -f helm/loki-values.yml
```

Then follow this guide: https://grafana.com/docs/loki/latest/visualize/grafana/#grafana-explore

Add this url: http://loki.monitoring.svc.cluster.local:3100
Add this heade: X-Scope-OrgID - sep