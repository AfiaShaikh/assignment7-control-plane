# Assignment 7 — Kubernetes architecture and Helm

This is a standalone Kubernetes/Helm project. Jenkins and a GitHub repository are not required to run it.
If you want to store it on GitHub, use a separate repository named **assignment-7-kubernetes-helm**.

## Start here

1. Extract as `C:\personal\afia\Assignment_7_Kubernetes_Helm`.
2. Start Docker Desktop with WSL integration enabled.
3. Follow `GUIDE.md` to install tools and create the local `assignment7` kind cluster.
4. Build/load image **assignment7-demo:1.0**, render and install the chart.
5. Build/load image **assignment7-demo:2.0**, then upgrade to two replicas.
6. Capture evidence and uninstall the Helm release.

All required application code, Dockerfile and chart are included here. You do not need any files from Assignment 6.

| Path | Purpose |
| --- | --- |
| app.py / index.html | Flask application with version, message, hostname and /health endpoint |
| requirements.txt / Dockerfile | Container image build |
| kind/cluster.yaml | Independent local Kubernetes cluster |
| helm/myapp/ | Chart, default values, v2 overrides and Kubernetes templates |
| GUIDE.md | Full procedure, architecture explanation and troubleshooting |
| Submission_Notes.md | Aim, observations and viva notes |
| Evidence/README.md | Required screenshots and outputs |

Use context **kind-assignment7**, namespace **assignment7**, release **myrelease** and local port **8082** as documented.
The Flask development server is used for this local educational demonstration. A production deployment would use a production WSGI server and further configuration.
Internet is required for initial tool/image/package downloads. Record the actual deployed results on your machine; no execution screenshots are supplied.

References:
- https://kind.sigs.k8s.io/docs/user/quick-start/
- https://kubernetes.io/docs/concepts/overview/components/
- https://helm.sh/docs/intro/install/
- https://helm.sh/docs/intro/using_helm/
