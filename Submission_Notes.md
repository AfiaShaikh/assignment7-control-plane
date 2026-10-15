# Assignment 7 — submission notes

Student name: ____________________

PRN / roll number: ____________________

Date: ____________________


**Title:** Explore Kubernetes Container Orchestration and Deploy an Application Using Helm.

**Aim:** Identify Kubernetes components and manage an application using a Helm chart.

**Implementation:** kind runs a local single-node Kubernetes cluster inside Docker. Helm templates define a Flask Deployment and ClusterIP Service. A local image is loaded into kind and installed as a named release. Upgrade values select a second image version and increase replicas from one to two. Uninstall removes the release resources.

**Architecture:** kubectl and Helm communicate with the API server. Cluster configuration is stored in etcd. Controllers reconcile desired state and the scheduler assigns Pods to nodes. The node's kubelet uses containerd to run containers. A Service selects Ready application Pods by labels; kube-proxy provides Service traffic forwarding in this lab.

**Observation fields:**

| Item | Actual observation |
| --- | --- |
| Kubernetes / kind / Helm versions | Fill |
| Context / node readiness | Fill |
| Release name / namespace | Fill |
| Initial image / Ready replicas / revision | Fill |
| Upgraded image / Ready replicas / revision | Fill |
| State after uninstall | Fill |

**Conclusion to complete after execution:** Helm release ______ was installed in namespace ______. Upgrading to image ______ produced ______ Ready replicas. Uninstall removed ______. Evidence is attached in ______.


## Viva notes

| Question | Answer |
| --- | --- |
| Docker vs Kubernetes? | Docker builds/runs containers here; Kubernetes schedules, monitors and connects application workloads. |
| Pod vs Deployment? | A Pod runs one or more containers; a Deployment manages desired replicas and rolling updates through ReplicaSets. |
| What is a Service? | A stable network endpoint selecting a set of Pods by labels. |
| What is Helm? | A package/release manager that renders chart templates using values and submits Kubernetes resources. |
| Chart vs release? | A chart is the reusable package; a release is one named installation of that chart. |
| helm template vs helm install? | Template renders YAML locally; install creates release resources in a cluster. |
| Chart version vs appVersion vs image tag? | Chart version identifies the package; appVersion is descriptive metadata; the image tag selects the container image in this chart. |
| Upgrade vs rollback? | Upgrade applies a new release configuration; rollback restores an earlier configuration as a new revision. |
| Why kind load? | The Docker host and kind's internal container runtime have separate image stores. |
| Why not show two worker nodes? | The resource-efficient local cluster combines roles on one node; the architecture concepts extend to multi-node clusters. |

Attach screenshots from your own execution.
