# hmp-server

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

The backend for [HearMyPaper](https://github.com/staleread/hearmypaper)

## Local development

Install and start services via Docker Compose:

```bash
docker compose up
```

The API will be available at `http://localhost:8000`. OpenAPI docs at `http://localhost:8000/docs`.

### Cleanup

```bash
docker compose down -v
```

## Deployment

Kubernetes deployment is managed via Helm and ArgoCD. See the [infra repo](https://github.com/staleread/hmp-infra) for setup instructions.
