from secuml.exp.celery_app.app import app


class IterationTask(app.Task):
    iteration_object = None


@app.task(base=IterationTask, bind=True, ignore_result=True,
          queue='SecuMLActiveLearning')
def run_next_iter(self):
    self.iteration_object.run_next_iter()
