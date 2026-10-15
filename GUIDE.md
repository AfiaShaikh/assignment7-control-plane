# Assignment 7 — Kubernetes architecture and Helm

Extract this assignment separately to `C:\personal\afia\Assignment_7_Kubernetes_Helm`.
All commands run in Ubuntu WSL from this assignment root:

```bash
cd /mnt/c/personal/afia/Assignment_7_Kubernetes_Helm
```

This project has no dependency on Assignment 6 or Jenkins.
This lab creates its own **kind** cluster named `assignment7`. You do not need to enable Docker Desktop's separate Kubernetes feature.

## 1. Install command-line tools

Keep Docker Desktop running. For an x86-64 / AMD64 WSL laptop:

```bash
uname -m
sudo apt-get update
sudo apt-get install -y curl ca-certificates
```

If `uname -m` returns `x86_64`, install kind with:

```bash
curl -fLo /tmp/kind-assignment7 https://kind.sigs.k8s.io/dl/v0.33.0/kind-linux-amd64
sudo install -m 0755 /tmp/kind-assignment7 /usr/local/bin/kind
```

For `aarch64`, substitute `kind-linux-arm64`. If kind is already installed, keep it and record `kind version` instead of replacing it.

Install kubectl if it is not already available:

```bash
KUBECTL_VERSION="$(curl -fsSL https://dl.k8s.io/release/stable.txt)"
curl -fLo /tmp/kubectl-assignment7 "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
curl -fLo /tmp/kubectl-assignment7.sha256 "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256"
printf '%s  %s\n' "$(cat /tmp/kubectl-assignment7.sha256)" /tmp/kubectl-assignment7 | sha256sum --check
sudo install -m 0755 /tmp/kubectl-assignment7 /usr/local/bin/kubectl
```

For ARM64 change both `linux/amd64` URL segments to `linux/arm64`.
Use a kubectl release within one minor version of your Kubernetes API server; the current kind release and current stable client are intended for this fresh lab setup.

Install Helm if missing, using its official installer:

```bash
curl -fsSL -o /tmp/get-helm-assignment7.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4
less /tmp/get-helm-assignment7.sh
bash /tmp/get-helm-assignment7.sh
```

Press `q` to exit `less`. Existing Helm 3 also supports the chart and the core commands used below; you do not need to replace it to finish this assignment.

```bash
docker version
kind version
kubectl version --client
helm version
```

Capture this output to record your actual versions.

## 2. Create the local Kubernetes cluster

```bash
kind create cluster --config kind/cluster.yaml --wait 180s
kubectl config current-context
kubectl --context kind-assignment7 get nodes -o wide
kubectl --context kind-assignment7 cluster-info
```

Use context **kind-assignment7** for this lab. Before proceeding:

```bash
kubectl config use-context kind-assignment7
kubectl get pods -n kube-system
```

Wait for the node to become Ready and system Pods to run. Initial image downloads take time.
If the named cluster already exists, use `kind get clusters` and switch context; do not delete it just to retry the next step.

## 3. Inspect architecture

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
kubectl get deployments -n kube-system
```

| Component | Role | Where to identify it in this lab |
| --- | --- | --- |
| API server | Receives Kubernetes API requests | `kube-apiserver-assignment7-control-plane` Pod |
| etcd | Stores cluster state | `etcd-assignment7-control-plane` Pod |
| Scheduler | Chooses a node for each pending Pod | `kube-scheduler-assignment7-control-plane` Pod |
| Controller manager | Reconciles desired and actual state | `kube-controller-manager-assignment7-control-plane` Pod |
| kubelet | Starts and monitors Pods on its node | Process in the kind node, not a separate application Pod |
| kube-proxy | Implements Service network forwarding in this setup | `kube-proxy-...` Pod |
| containerd | Runs the application containers | Container runtime inside the kind node |
| CoreDNS | Cluster DNS and Service-name resolution | `coredns-...` Pods |

Optional process/runtime inspection:

```bash
docker exec assignment7-control-plane crictl info
```

The single kind node runs both control-plane components and application workloads. Kubernetes can use separate workers, but this smaller lab does not create them. Docker runs the node container; containerd inside that node runs the Kubernetes workload containers.

## 4. Explore a generated chart, then use the supplied application chart

The assignment asks you to create a chart. Generate an example in a temporary folder:

```bash
mkdir -p /tmp/assignment7-chart-example
helm create /tmp/assignment7-chart-example/myapp-example
ls -R /tmp/assignment7-chart-example/myapp-example
cat /tmp/assignment7-chart-example/myapp-example/Chart.yaml
```

Capture its structure. This is an unmodified Helm starter example, not the chart we deploy.
Our supplied chart is `helm/myapp` and is already adapted to the Flask image; do not overwrite it with `helm create`.

| File | Purpose |
| --- | --- |
| Chart.yaml | Chart name, description, chart version and appVersion metadata |
| values.yaml | Default image tag, replicas, resources, Service and page message |
| values-v2.yaml | Overrides for the upgrade demonstration |
| templates/deployment.yaml | Template for Pods and the Deployment |
| templates/service.yaml | Stable Service endpoint selecting those Pods |
| templates/_helpers.tpl | Reusable resource names and labels |
| templates/NOTES.txt | Post-install instructions |
| charts/ | Optional dependency charts; none required here |

## 5. Build and load version 1 into kind

```bash
docker build --build-arg APP_VERSION=1.0 -t assignment7-demo:1.0 .
kind load docker-image assignment7-demo:1.0 --name assignment7
```

Loading is essential: an image built in Docker Desktop is not automatically available to containerd inside kind.
The chart uses `IfNotPresent`, so it can use this local image without a container registry.

## 6. Render, then install

```bash
mkdir -p Evidence
helm lint ./helm/myapp
helm template myrelease ./helm/myapp --namespace assignment7 > Evidence/helm-rendered-v1.yaml
cat Evidence/helm-rendered-v1.yaml
helm install myrelease ./helm/myapp --namespace assignment7 --create-namespace --wait --timeout 180s
helm list -n assignment7
helm status myrelease -n assignment7
kubectl -n assignment7 get deployments,pods,services -o wide
```

Rendering produces Kubernetes YAML without deploying. Installation submits it to the Kubernetes API and creates a named Helm release.
Expected resource names are `myrelease-myapp` for both Deployment and Service.

If `myrelease` already exists, inspect `helm list -n assignment7` before deciding whether to continue with upgrade. Do not run install repeatedly with the same release name.

## 7. Open the running application

In a separate WSL terminal, enter the project folder and run:

```bash
kubectl --context kind-assignment7 -n assignment7 port-forward svc/myrelease-myapp 8082:80
```

Leave it running. Open **http://localhost:8082** in Windows Chrome/Edge.
You should see version **1.0**, the release-v1 message and a Pod hostname.
In another WSL terminal:

```bash
curl -fsS http://localhost:8082/health
```

Capture the page and workload state. We use ClusterIP plus local port-forward for predictable WSL access. This demonstrates the required Service without NodePort host-routing setup.

## 8. Upgrade to version 2 and two replicas

Build a distinct image so the upgrade changes actual container contents:

```bash
docker build --build-arg APP_VERSION=2.0 -t assignment7-demo:2.0 .
kind load docker-image assignment7-demo:2.0 --name assignment7
helm upgrade myrelease ./helm/myapp -n assignment7 -f ./helm/myapp/values-v2.yaml --wait --timeout 180s
helm history myrelease -n assignment7
helm get values myrelease -n assignment7
kubectl -n assignment7 get deployments,pods,services -o wide
kubectl -n assignment7 get deployment myrelease-myapp -o jsonpath='{.spec.template.spec.containers[0].image}'
```

After the rollout settles, expect two Ready replicas running `assignment7-demo:2.0`.
Stop the old port-forward with Ctrl+C and rerun the port-forward command from step 7, because its selected Pod may have been replaced during upgrade.
Reload the browser: version **2.0** and the changed message should appear.
The changed image tag is the runtime application version; `Chart.yaml`'s `appVersion` is chart metadata and does not automatically select an image.
You can explain these as separate concepts during the viva. A published v2 chart would also update its metadata.

Port-forward selects a Pod behind the Service. Repeated requests through this single forwarding session do not demonstrate load balancing across both Pods.

## 9. Optional rollback

Capture upgrade evidence first. Then:

```bash
helm rollback myrelease 1 -n assignment7 --wait --timeout 180s
helm history myrelease -n assignment7
kubectl -n assignment7 get deployments,pods
```

Rollback restores revision 1's configuration as a new release revision. Restart port-forward after replacement of its selected Pod to view version 1 again.

## 10. Record evidence, then uninstall

Save these before removal:

```bash
helm history myrelease -n assignment7 > Evidence/helm-history.txt
kubectl -n assignment7 get deployments,pods,services -o wide > Evidence/workloads-before-uninstall.txt
```

Stop the port-forward with Ctrl+C, then:

```bash
helm uninstall myrelease -n assignment7
helm list -n assignment7
kubectl -n assignment7 get deployments,pods,services
```

The release's Deployment, Pods and Service should be gone. The namespace and kind cluster remain.
After saving all required evidence, optionally remove only this lab cluster:

```bash
kind delete cluster --name assignment7
```

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `kubectl` connection refused | Check `kind get clusters`, Docker Desktop, and context `kind-assignment7`. |
| ImagePullBackOff / ErrImagePull | Match the exact image tag and run `kind load docker-image ... --name assignment7`; inspect `kubectl describe pod`. |
| Pod Pending | Inspect `kubectl -n assignment7 describe pod POD_NAME` and node resources; stop other unused containers if memory is tight. |
| CrashLoopBackOff | Inspect `kubectl -n assignment7 logs POD_NAME` and describe output. |
| Helm install timeout | Run `kubectl -n assignment7 get pods` and describe the affected Pod; fix the cause before retrying with `helm upgrade --install`. |
| Port 8082 already in use | Stop the earlier port-forward, or use `8083:80` and open localhost:8083. |
| Page disappears during upgrade | Its forwarded Pod was replaced; restart the port-forward after the rollout. |
| Upgrade still shows v1 | Confirm the Deployment image is `assignment7-demo:2.0`, that v2 was loaded, and that the browser uses a newly started forward. |

Commands using `POD_NAME` require the actual Pod name from `kubectl get pods`.
