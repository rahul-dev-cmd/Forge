FROM python:3.13-slim AS builder

WORKDIR /app

# Fetch the official astral uv binary layer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvbin/uv

# Copy dependencies config
COPY pyproject.toml README.md ./

# Create virtual environment and install dependencies
RUN /uvbin/uv venv .venv && \
    /uvbin/uv pip install --no-cache -r pyproject.toml

FROM python:3.13-slim AS runner

WORKDIR /app

# Copy compiled virtualenv and app source codes
COPY --from=builder /app/.venv /app/.venv
COPY app /app/app
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini

# Bind virtualenv bin path to executables search list
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
