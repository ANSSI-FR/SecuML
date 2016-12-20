## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

from SecuML.Data.Dataset import Dataset
from SecuML.Experiment import ExperimentFactory
from SecuML.Experiment.Experiment import Experiment
from SecuML.SupervisedLearning.Configuration import SupervisedLearningConfFactory
from SecuML.Tools import mysql_tools

class SupervisedLearningExperiment(Experiment):

    def __init__(self, project, dataset, db, cursor):
        Experiment.__init__(self, project, dataset, db, cursor)
        self.kind = 'SupervisedLearning'

    def setSupervisedLearningConf(self, supervised_learning_conf):
        self.supervised_learning_conf = supervised_learning_conf

    def generateSuffix(self):
        suffix  = self.supervised_learning_conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, db, cursor):
        experiment = SupervisedLearningExperiment(obj['project'], obj['dataset'], db, cursor)
        Experiment.expParamFromJson(experiment, obj)
        supervised_learning_conf = SupervisedLearningConfFactory.getFactory().fromJson(
                obj['supervised_learning_conf'], experiment)
        experiment.setSupervisedLearningConf(supervised_learning_conf)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'SupervisedLearningExperiment'
        conf['supervised_learning_conf'] = self.supervised_learning_conf.toJson()
        return conf

    def webTemplate(self):
        return 'SupervisedLearning/supervised_learning.html'

ExperimentFactory.getFactory().registerClass('SupervisedLearningExperiment', SupervisedLearningExperiment)
