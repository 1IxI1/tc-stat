from loguru import logger
from prometheus_client import start_http_server

# metrics are defined in workers for each method


def start_prometheus():
    port = 9091
    host = "0.0.0.0"
    logger.info(f"Starting Prometheus exporter on {host}:{port}")

    start_http_server(port, host)
