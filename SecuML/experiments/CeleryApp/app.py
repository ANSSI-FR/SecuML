from celery import Celery
from celery.bin import worker

# instantiate Celery object
app = Celery(include=['SecuML.experiments.ActiveLearning.CeleryTasks'])

# import celery config file
app.config_from_object('SecuML.experiments.CeleryApp.celery_config')

secumlworker = worker.worker(app=app)

if __name__ == '__main__':
    app.start()
