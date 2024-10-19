FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY ./pyproject.toml ./uv.lock /
COPY ./main.py /main.py

RUN uv sync --frozen --no-cache --no-dev

RUN mkdir -p /tmp/shm && mkdir /.local

ENV PORT=8080
EXPOSE 8080

ENTRYPOINT [".venv/bin/uvicorn", "main:app", "--host",  "0.0.0.0", "--port", "8080"]
