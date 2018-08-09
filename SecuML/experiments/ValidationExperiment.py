# SecuML
# Copyright (C) 2016-2018  ANSSI
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

from SecuML.core.Configuration import Configuration
from SecuML.experiments import db_tables
from SecuML.experiments import ExperimentFactory
from SecuML.experiments.Experiment import Experiment


class ValidationExperiment(Experiment):

    def getKind(self):
        return 'Validation'

    def generateSuffix(self):
        suffix = ''
        return suffix

    def _checkConf(self):
        if not db_tables.hasGroundTruth(self):
            self.conf.logger.warning(
                'The validation dataset does not have ground-truth.')

    @staticmethod
    def fromJson(obj, session):
        experiment = ValidationExperiment(obj['project'], obj['dataset'],
                                          session, create=False)
        Experiment.expParamFromJson(experiment, obj, Configuration())
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ValidationExperiment'
        return conf


ExperimentFactory.getFactory().registerClass('ValidationExperiment',
                                             ValidationExperiment)
