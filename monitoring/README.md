# Setup a monitoring stack for K8s

## Installing the observability addon for MicroK8s

1. Create a new namespace: `kubectl create namespace observability`
2. Create a new TLS certificate by following these commands:

```bash
cd /home/swtp/certs

# create a new cert without a password
openssl req -x509 -newkey rsa:4096 -keyout grafana-key.pem -out grafana-cert.pem -sha256 -days 365 -nodes
# Country Name: DE
# State: Saxony
# Locality: Leipzig
# Organization Name: SEP Gruppe 16
# Organizational Unit Name: Grafana
# Common Name: <ip of server>

# create K8s secret
kubectl -n observability create secret tls grafana-tls --cert=./grafana-cert.pem --key=./grafana-key.pem

cd
```

3. Copy the file `stack-values.yml` to the server
4. Run: `sudo microk8s enable observability --kube-prometheus-stack-values=stack-values.yml`
5. Grafana should now be reachable at `grafana.sep.internal` if you map this domain to the servers IP on your local host
6. The default credentials are: `admin/prom-operator` (user/password)

In Grafana, edit the Loki integration by setting this header: `X-Scope-OrgID - sep`

# Install Nosferatu

Create these accounts: `nosferatu` (verwaltung), `nosferatu_standort` (standortleitung) and `nosferatu_kueche` (kuechenleitung).
Let them have the same password and save it as a secret:

```bash
kubectl create secret generic nosferatu --from-literal=PASSWORD=supersecret
```

Create a secret with the target URL:

```bash
kubectl create secret generic nosferatu-base-url --from-literal=BASE_URL="https://<ip-address>/"
```

Do not forget the trailing slash!

Then deploy the pod. This is just the backend pod but it will run the script instead of the application:

```bash
kubectl apply -f monitoring/nosferatu.yml
```
