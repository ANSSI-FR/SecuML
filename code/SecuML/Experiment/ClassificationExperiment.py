## SecuML
## Copyright (C) 2016-2017  ANSSI
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

from sklearn.externals import joblib

from SecuML.Experiment import ExperimentFactory
from SecuML.Experiment.Experiment import Experiment
from SecuML.Classification.Configuration import ClassifierConfFactory

class ClassificationExperiment(Experiment):

    def __init__(self, project, dataset, session, experiment_name = None,
                 parent = None):
        Experiment.__init__(self, project, dataset, session,
                experiment_name = experiment_name,
                parent = parent)
        self.kind = 'Classification'

    def setClassifierConf(self, classification_conf):
        self.classification_conf = classification_conf

    def generateSuffix(self):
        suffix  = self.classification_conf.generateSuffix()
        return suffix

    def getModelPipeline(self):
        experiment_dir = self.getOutputDirectory()
        pipeline = joblib.load(experiment_dir + '/model/model.out')
        return pipeline

    @staticmethod
    def fromJson(obj, session):
        experiment = ClassificationExperiment(obj['project'], obj['dataset'], session)
        Experiment.expParamFromJson(experiment, obj)
        classification_conf = ClassifierConfFactory.getFactory().fromJson(
                obj['classification_conf'], experiment)
        experiment.setClassifierConf(classification_conf)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ClassificationExperiment'
        conf['classification_conf'] = self.classification_conf.toJson()
        return conf

    def webTemplate(self):
        return 'Classification/classification.html'

ExperimentFactory.getFactory().registerClass('ClassificationExperiment',
                                             ClassificationExperiment)
