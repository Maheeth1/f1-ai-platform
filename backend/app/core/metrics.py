from prometheus_client import Counter, Histogram

# Business metrics
PREDICTIONS_COUNTER = Counter(
    "f1_predictions_total",
    "Total number of predictions requested",
    ["target", "version", "status"]
)

PREDICTION_LATENCY = Histogram(
    "f1_prediction_latency_seconds",
    "Latency of the internal model inference process",
    ["target"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

CACHE_EVENTS = Counter(
    "f1_cache_events_total",
    "Total cache hit and miss events",
    ["type"]  # 'hit' or 'miss'
)
