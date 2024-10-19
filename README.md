# 💩 Poopyrus API

We don't take shit.. we track it.

## Development

Install dependencies.

```bash
$ uv sync

Resolved 44 packages in 0.81ms
Audited 42 packages in 0.04ms
```

Start the local development server.

```bash
$ fastapi dev main.py

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Deployment

Build docker container with new version.

```bash
$ gcloud builds submit --tag us-east1-docker.pkg.dev/homy-408915/poopyrus/poopyrus-api:1.0.0
```

Update [deployment.yaml](./infra/deployment.yaml) to new image.

Apply new deployment update.

```bash
$ kubectl apply -f infra/deployment.yaml

```
