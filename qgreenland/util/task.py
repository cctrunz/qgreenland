from qgreenland.config import CONFIG
from qgreenland.tasks.layers import INGEST_TASKS


def generate_layer_tasks():
    """Generate a list of pre-configured tasks based on layer configuration.

    Instead of calling tasks now, we return a list of callables with the
    arguments already populated.
    """
    tasks = []

    for cfg in CONFIG['layers'].values():
        task = INGEST_TASKS[cfg['ingest_task']]
        kwargs = {'layer_id': cfg['id']}
        kwargs.update(cfg.get('ingest_task_kwargs', {}))

        tasks.append(task(**kwargs))

    return tasks
