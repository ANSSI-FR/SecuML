# SecuML
# Copyright (C) 2018  ANSSI
#
# SecuML is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# SecuML is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with SecuML. If not, see <http://www.gnu.org/licenses/>.

from SecuML.experiments.CeleryApp.app import app


class IterationTask(app.Task):
    iteration_object = None


@app.task(base=IterationTask, bind=True,
          ignore_result=True, queue='SecuMLActiveLearning')
def runNextIteration(self):
    self.iteration_object.runNextIteration()


@app.task(base=IterationTask, bind=True,
          ignore_result=False, queue='SecuMLActiveLearning')
def checkAnnotationQueriesAnswered(self):
    return self.iteration_object.checkAnnotationQueriesAnswered()
