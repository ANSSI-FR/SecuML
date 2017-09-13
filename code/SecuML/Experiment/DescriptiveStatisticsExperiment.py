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

class DescriptiveStatisticsExperiment(Experiment):

    def __init__(self, project, dataset, session):
        Experiment.__init__(self, project, dataset, session)
        self.kind = 'DescriptiveStatistics'

    def setClassifierConf(self, classification_conf):
        self.classification_conf = classification_conf

    def generateSuffix(self):
        return ''

    @staticmethod
    def fromJson(obj, session):
        experiment = DescriptiveStatisticsExperiment(obj['project'], obj['dataset'], session)
        Experiment.expParamFromJson(experiment, obj)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'DescriptiveStatisticsExperiment'
        return conf

    def webTemplate(self):
        return 'DescriptiveStatistics/descriptive_statistics.html'

ExperimentFactory.getFactory().registerClass('DescriptiveStatisticsExperiment', DescriptiveStatisticsExperiment)
