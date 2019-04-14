
import os

from flask import current_app

from recordit.extensions import scheduler


@scheduler.task('interval', id='clear_cache', weeks=1)
def clear_cache():
    with scheduler.app.app_context():
        for root, _, files in os.walk(current_app.config['FILE_CACHE_PATH']):
            for file in files:
                if file == '.gitkeep':
                    continue
                path = os.path.join(root, file)
                os.remove(path)
