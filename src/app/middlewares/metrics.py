import time
from collections import namedtuple

from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    multiprocess,
)
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import PATHES_TO_SKIP_METRICS_FOR, settings

base_http_request_metric_labels = namedtuple(
    'BaseHTTPRequestMetricLabels',
    ('app', 'path', 'method', 'status_code'),
)
APP_HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'app_http_request_duration_seconds',
    'App HTTP request duration, seconds',
    base_http_request_metric_labels._fields,
)
APP_HTTP_REQUEST_COUNT = Counter(
    'app_http_request_count',
    'App HTTP request count',
    base_http_request_metric_labels._fields,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in PATHES_TO_SKIP_METRICS_FOR:
            return await call_next(request)

        exception = None
        try:
            start_at = time.perf_counter()
            response = await call_next(request)
        except Exception as e:
            exception = e

        end_at = time.perf_counter()

        if exception:
            status_code = 500
        else:
            status_code = response.status_code

        labels = base_http_request_metric_labels(
            app=settings.APP_NAME,
            path=path,
            method=request.method,
            status_code=status_code,
        )
        APP_HTTP_REQUEST_DURATION_SECONDS.labels(*labels).observe(end_at - start_at)
        APP_HTTP_REQUEST_COUNT.labels(*labels).inc()

        if exception:
            raise exception

        return response


def metrics_route(_: Request):
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(
        generate_latest(registry),
        status_code=200,
        headers={'Content-Type': CONTENT_TYPE_LATEST},
    )
