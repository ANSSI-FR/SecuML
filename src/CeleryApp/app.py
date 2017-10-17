from __future__ import absolute_import

from celery import Celery
from celery.bin import worker

#instantiate Celery object
app = Celery(include=['CeleryApp.activeLearningTasks'])

# import celery config file
app.config_from_object('CeleryApp.celeryconfig')

secumlworker = worker.worker(app=app)

if __name__ == '__main__':
	app.start()
