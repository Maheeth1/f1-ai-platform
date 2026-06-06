# F1 AI Platform Backend

This is the production-grade FastAPI backend for the F1 AI Prediction Platform. It provides modular service-oriented architecture for predicting Formula 1 race positions.

## Architecture

The backend follows a modular, layer-based architecture:

```text
backend/
├── models/
│   ├── registry.json            # JSON store for model versions and metadata
│   ├── laptime/                 # Models targeting laptime
│   ├── gridposition/            # Models targeting gridposition
│   └── simulation/              # Models targeting race simulation
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py        # Health check routes
│   │   │   ├── prediction.py    # Prediction endpoints
│   │   │   ├── models.py        # Model registry and metadata endpoints
│   │   │   └── metadata.py      # Application metadata
│   │   └── dependencies.py      # FastAPI dependencies
│   ├── services/
│   │   ├── inference_service.py # Core prediction logic
│   │   ├── model_registry.py    # Singleton registry for models
│   │   └── huggingface_service.py # Model downloading logic
│   ├── schemas/
│   │   ├── prediction.py        # Prediction request schemas
│   │   └── registry.py          # Registry and metadata schemas
│   ├── core/
│   │   ├── config.py            # Centralized settings
│   │   └── logger.py            # Structured logging
│   └── main.py                  # App factory and lifespan
```

## Model Registry

The backend now uses a robust model registry layer. Models can be registered for different targets (e.g., `laptime`, `gridposition`, `simulation`) and tracked using versions.

### Registry Endpoints
- **GET `/models`**: Fetches the entire registry state (all targets, versions, metrics, and metadata).
- **GET `/models/active`**: Fetches the currently active model information for all targets.
- **POST `/models/register`**: Registers a new model version into the registry.
- **POST `/models/switch`**: Switches the active model to another registered version.
- **POST `/models/rollback/{target}`**: Rolls back the active model for a target to its previous active version.

## Running the Application

1. Ensure dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server using Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```

3. The API will be available at `http://127.0.0.1:8000`. You can test the health at `/health` and view documentation at `/docs`.
