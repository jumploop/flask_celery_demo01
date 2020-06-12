import time
from flask import Flask
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/2'

# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])


def make_celery(app):
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'],backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@celery.task()
def add_together(a, b):
    time.sleep(10)
    return a + b


@app.route('/')
def hello_world():
    result = add_together.delay(23, 42)
    print(result)
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
