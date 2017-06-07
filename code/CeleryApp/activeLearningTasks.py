from CeleryApp.app import app

class IterationTask(app.Task):
    iteration_object = None

@app.task(base=IterationTask, bind=True,
          ignore_result=True, queue='SecuMLActiveLearning')
def runNextIteration(self):
    self.iteration_object.runNextIteration()
