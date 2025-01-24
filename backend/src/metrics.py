from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics.for_app_factory(path="/api/metrics")


def init_metrics(app):
    """Initialize the metrics endpoint with the given Flask app."""

    metrics.init_app(app)
