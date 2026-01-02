# Étape 1: Construction - Installer les dépendances et construire l'application
FROM python:3.11-slim AS builder

# Définir le répertoire de travail
WORKDIR /app

# Installer Poetry
RUN pip install poetry

# Copier les fichiers de configuration du projet
COPY pyproject.toml poetry.lock* ./

# Installer les dépendances
RUN poetry install --no-root --only main

# Étape 2: Production - Environnement d'exécution minimal
FROM python:3.11-slim AS production

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances installées depuis l'étape de construction
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/poetry /usr/local/bin/poetry

# Copier le code source de l'application
COPY src/ src/
COPY scripts/ scripts/
COPY configs/ configs/

# Exposer le port de l'API (FastAPI)
EXPOSE 8000

# Définir la variable d'environnement pour l'API
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO

# Commande par défaut pour démarrer l'API
CMD ["uvicorn", "pts.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
