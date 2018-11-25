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

from SecuML.core.features_analysis.FeaturesAnalysis import FeaturesAnalysis
from SecuML.exp import ExperimentFactory
from SecuML.exp.db_tables import FeaturesAnalysisExpAlchemy
from SecuML.exp.Experiment import Experiment

from .FeaturesAnalysisConf import FeaturesAnalysisConf


class FeaturesAnalysisExperiment(Experiment):

    def add_to_db(self):
        Experiment.add_to_db(self)
        dataset_features_id = self.exp_conf.features_conf.dataset_features_id
        annotations_file = self.exp_conf.annotations_conf.annotations_filename
        stats_exp = FeaturesAnalysisExpAlchemy(id=self.experiment_id,
                                       dataset_features_id=dataset_features_id,
                                       annotations_filename=annotations_file)
        self.session.add(stats_exp)
        self.session.flush()

    def run(self):
        Experiment.run(self)
        stats = FeaturesAnalysis(self.getInstances())
        stats.compute()
        stats.export(self.output_dir())

    def webTemplate(self):
        return 'features_analysis/main.html'


ExperimentFactory.getFactory().register('FeaturesAnalysis',
                                        FeaturesAnalysisExperiment,
                                        FeaturesAnalysisConf)
