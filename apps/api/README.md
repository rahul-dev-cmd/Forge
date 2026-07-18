# Forge API Backend

This is the FastAPI backend application for Forge.

## Setup & Running

1. Ensure Python 3.13+ is installed.
2. Initialize virtual environment:
   ```bash
   uv venv
   ```
3. Install dependencies:
   ```bash
   uv pip install -e .
   ```
4. Run application:
   ```bash
   uvicorn app.main:app --reload
   ```
