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

from SecuML.Experiment import ExperimentFactory
from SecuML.Experiment.Experiment import Experiment
from SecuML.UnsupervisedLearning.Configuration import ClusteringConfFactory

class ClusteringExperiment(Experiment):

    def __init__(self, project, dataset, db, cursor, conf,
            experiment_name = None, experiment_label = None,
            parent = None):
        Experiment.__init__(self, project, dataset, db, cursor,
                experiment_name = experiment_name,
                experiment_label = experiment_label,
                parent = parent)
        self.kind = 'Clustering'
        self.conf = conf

    def generateSuffix(self):
        suffix  = ''
        suffix += self.conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, db, cursor):
        conf = ClusteringConfFactory.getFactory().fromJson(obj['conf'])
        experiment = ClusteringExperiment(
                obj['project'], obj['dataset'], db, cursor,
                conf)
        Experiment.expParamFromJson(experiment, obj)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ClusteringExperiment'
        conf['conf'] = self.conf.toJson()
        return conf

    def webTemplate(self):
        return 'UnsupervisedLearning/clustering.html'

ExperimentFactory.getFactory().registerClass('ClusteringExperiment', ClusteringExperiment)
