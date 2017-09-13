## SecuML
## Copyright (C) 2017  ANSSI
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

class TrueLabelsExperiment(Experiment):

    def __init__(self, project, dataset, session):
        Experiment.__init__(self, project, dataset, session)
        self.experiment_name = 'true_labels'
        self.kind            = 'TrueLabels'

    def generateSuffix(self):
        return ''

    @staticmethod
    def fromJson(obj, session):
        experiment = TrueLabelsExperiment(obj['project'], obj['dataset'], session)
        Experiment.expParamFromJson(experiment, obj)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'TrueLabelsExperiment'
        return conf

ExperimentFactory.getFactory().registerClass('TrueLabelsExperiment', TrueLabelsExperiment)
