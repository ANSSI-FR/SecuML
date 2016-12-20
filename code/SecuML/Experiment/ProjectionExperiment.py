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
from SecuML.UnsupervisedLearning.Configuration import ProjectionConfFactory
from SecuML.UnsupervisedLearning.Configuration.SemiSupervisedProjectionConfiguration \
        import SemiSupervisedProjectionConfiguration

class ProjectionExperiment(Experiment):

    def __init__(self, project, dataset, db, cursor, conf,
            experiment_name = None, experiment_label = None,
            parent = None):
        Experiment.__init__(self, project, dataset, db, cursor,
                experiment_name = experiment_name,
                experiment_label = experiment_label,
                parent = parent)
        self.kind = 'Projection'
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

    def setFeaturesFilenames(self, features_filenames):
        Experiment.setFeaturesFilenames(self, features_filenames)
        # Set the number of components to the number of features
        # if it has not been specified before
        if self.conf.num_components is None:
            num_features = 0
            for filename in self.getFeaturesFilesFullpaths():
                with open(filename, 'r') as f:
                    header = f.readline().split(',')
                    num_features += len(header) - 1
            self.conf.num_components = num_features

    @staticmethod
    def fromJson(obj, db, cursor):
        conf = ProjectionConfFactory.getFactory().fromJson(obj['conf'])
        experiment = ProjectionExperiment(
                obj['project'], obj['dataset'], db, cursor,
                conf)
        Experiment.expParamFromJson(experiment, obj)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ProjectionExperiment'
        conf['conf'] = self.conf.toJson()
        return conf

    def webTemplate(self):
        return 'UnsupervisedLearning/projection.html'

ExperimentFactory.getFactory().registerClass('ProjectionExperiment', ProjectionExperiment)
