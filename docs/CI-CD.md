# CI/CD

## Permissions and Secrets

- Workflow permissions: packages: write, contents: read
- `DO_ACCESS_TOKEN`: DigitalOcean API token
- `DO_APP_ID_DEV`: DigitalOcean App ID for development environment (deploys on push to main)
- `DO_APP_ID_PROD`: DigitalOcean App ID for production environment (deploys on push to prod)

## Local checks

```bash
pip install -e .
pip install ruff mypy
ruff check .
mypy .
```

## Image tags

- main -> ghcr.io/<OWNER>/hmp-server:dev and :dev-<sha>
- prod -> ghcr.io/<OWNER>/hmp-server:prod and :prod-<sha>

After publish, a DO App Platform deployment is triggered on the corresponding environment.
