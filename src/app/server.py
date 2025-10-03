import logging
import os
import shutil

import uvicorn

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_prometheus_multiproc_dir():
    """
    Reason: https://prometheus.github.io/client_python/multiprocess/

    Note that we don't call prometheus_client.multiprocess.mark_process_dead(dead_worker_pid).
    It does nothing since we don't collect metrics of the gauge type.
    """
    env_var_name = 'PROMETHEUS_MULTIPROC_DIR'
    dir_perm = 0o744

    path = os.getenv(env_var_name)
    if not path:
        path = '/tmp/prometheus_multiproc_dir'
        os.environ[env_var_name] = path
        logger.info(
            'The %s directory will be used to store Prometheus metrics. Added to env vars.',
            path,
        )

    if os.path.isdir(path):
        shutil.rmtree(path)
        logger.info('The old %s directory was deleted.', path)

    os.mkdir(path, mode=dir_perm)
    logger.info('The new %s directory was created.', path)


if __name__ == '__main__':
    setup_prometheus_multiproc_dir()
    uvicorn.run(
        app='app.main:app',
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        workers=settings.UVICORN_WORKERS,
    )
