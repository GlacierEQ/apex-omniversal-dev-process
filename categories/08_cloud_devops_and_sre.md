# ☁️ CATEGORY 08: Cloud, DevOps & Site Reliability Engineering (SRE)

## 1. Scope & Architectural Mandate
Governs multi-cloud deployment topologies, container virtualization, infrastructure-as-code (IaC), automated CI/CD release pipelines, zero-downtime rollouts, and telemetry watchdogs.

- **Domains**: Docker containerization, Kubernetes orchestration, Terraform / OpenTofu, GitHub Actions CI/CD workflows, blue/green and canary deployments, multi-cloud disaster recovery.
- **Key Constraints**: Zero deployment downtime, automated rollback within $< 30\text{s}$ upon health probe failure, strictly air-gapped secret injection, non-root container sandboxes.

---

## 2. Polyglot Technology Stack
- **IaC & Config**: Terraform, Helm, Dockerfile, YAML, Bash / Zsh.
- **Platforms**: AWS, Google Cloud Platform (GCP), Vercel, Supabase, Cloudflare Workers.
- **CI/CD & Monitoring**: GitHub Actions, Prometheus, Grafana, OpenTelemetry (OTel).

---

## 3. Core Invariants & Fail-Closed Boundaries
1. **Immutable Artifact Invariant**:
   - Containers and deployment bundles must be built once, hashed with SHA-256, and promoted across environments (Dev $\to$ Staging $\to$ Prod) without recompilation.
2. **Secret Non-Leakage**:
   - Zero hardcoded secrets in repository code or container images. Secrets are injected at runtime via ephemeral vault tokens or environment secret stores.
3. **Refusal Reason Codes**:
   - `ERR_SRE_HEALTH_CHECK_FAILED`: Deployment container failed readiness probe.
   - `ERR_SRE_ROLLBACK_TRIGGERED`: Automated canary error rate breached SLA threshold.
   - `ERR_SRE_SECRET_MISSING`: Required environment secret variable absent at bootup.
   - `ERR_SRE_CONTAINER_ROOT_PROHIBITED`: Dockerfile runs as root user (`UID 0`).

---

## 4. Stage-by-Stage Implementation Guide

### Stage 0: Contracting
- Define availability targets (e.g., 99.99% uptime), error budgets, and Recovery Time Objective (RTO) / Recovery Point Objective (RPO).
- Specify cloud provider redundancy (e.g., multi-region or multi-cloud fallback).

### Stage 1: Architectural Modeling
- Design deployment topologies: VPC networks, ingress load balancers, private subnets.
- Specify zero-downtime rolling update strategy (e.g., maxSurge: 25%, maxUnavailable: 0%).

### Stage 2: Pro-Code Implementation
- Write multi-stage, rootless Dockerfiles with minimal base images (Alpine or Distroless).
- Construct declarative GitHub Actions workflows running automated tests and security linters.

### Stage 3: Adversarial Verification
- Simulate container crash during rolling update; verify zero dropped HTTP connections.
- Scan container images with Trivy / Grype; assert zero Critical or High vulnerabilities.

---

## 5. Reference Pattern: Rootless, Multi-Stage Dockerfile Standard
```dockerfile
# Stage 1: Build
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production Runtime
FROM python:3.12-slim-bookworm AS runner
WORKDIR /app

# Enforce non-root security invariant
RUN groupadd -g 10001 appgroup && useradd -u 10001 -g appgroup -s /sbin/nologin appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appgroup src/ ./src/

ENV PATH=/home/appuser/.local/bin:$PATH
USER 10001:10001

EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=2)" || exit 1

ENTRYPOINT ["python3", "-m", "src.main"]
```
