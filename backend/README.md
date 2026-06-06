# F1 AI Platform Backend

This is the production-grade FastAPI backend for the F1 AI Prediction Platform. It provides modular service-oriented architecture for predicting Formula 1 race positions.

## Architecture

The backend follows a modular, layer-based architecture:

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py       # Health check routes
│   │   │   ├── prediction.py   # Prediction endpoints
│   │   │   ├── models.py       # Model metadata endpoints
│   │   │   └── metadata.py     # Application metadata
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── services/
│   │   ├── inference_service.py # Core prediction logic
│   │   ├── model_registry.py    # Singleton model holder
│   │   └── huggingface_service.py # Model downloading logic
│   ├── schemas/
│   │   └── prediction.py        # Pydantic validation schemas
│   ├── core/
│   │   ├── config.py            # Centralized settings
│   │   └── logger.py            # Structured logging
│   └── main.py                  # App factory and lifespan
```

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
