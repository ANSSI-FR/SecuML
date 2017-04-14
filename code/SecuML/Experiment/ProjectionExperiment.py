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
from SecuML.Projection.Configuration import ProjectionConfFactory
from SecuML.Projection.Configuration.SemiSupervisedProjectionConfiguration \
        import SemiSupervisedProjectionConfiguration

class ProjectionExperiment(Experiment):

    def __init__(self, project, dataset, db, cursor,
            experiment_name = None, experiment_label = None,
            parent = None):
        Experiment.__init__(self, project, dataset, db, cursor,
                experiment_name = experiment_name,
                experiment_label = experiment_label,
                parent = parent)
        self.kind = 'Projection'

    def setConf(self, conf):
        self.conf = conf

    def generateSuffix(self):
        suffix  = ''
        suffix += self.conf.generateSuffix()
        return suffix

    def initLabels(self, labels_filename = None, overwrite = True):
        if isinstance(self.conf, SemiSupervisedProjectionConfiguration):
            if labels_filename is None:
                message  = 'Semi supervised projections require annotated instances. '
                message += 'labels_filename must be specified.'
                raise ValueError(message)
        Experiment.initLabels(self, labels_filename = labels_filename, overwrite = overwrite)

    @staticmethod
    def fromJson(obj, db, cursor):
        conf = ProjectionConfFactory.getFactory().fromJson(obj['conf'])
        experiment = ProjectionExperiment(
                obj['project'], obj['dataset'], db, cursor)
        Experiment.expParamFromJson(experiment, obj)
        experiment.setConf(conf)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ProjectionExperiment'
        conf['conf'] = self.conf.toJson()
        return conf

    def webTemplate(self):
        return 'Projection/projection.html'

ExperimentFactory.getFactory().registerClass('ProjectionExperiment', ProjectionExperiment)
