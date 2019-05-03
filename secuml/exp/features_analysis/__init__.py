# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from secuml.core.features_analysis import FeaturesAnalysis
from secuml.exp import experiment
from secuml.exp.tools.db_tables import FeaturesAnalysisExpAlchemy
from secuml.exp.experiment import Experiment

from .conf import FeaturesAnalysisConf


class FeaturesAnalysisExperiment(Experiment):

    def add_to_db(self):
        Experiment.add_to_db(self)
        features_set_id = self.exp_conf.features_conf.set_id
        annotations_file = self.exp_conf.annotations_conf.annotations_filename
        stats_exp = FeaturesAnalysisExpAlchemy(
                                       id=self.exp_id,
                                       features_set_id=features_set_id,
                                       annotations_filename=annotations_file)
        self.session.add(stats_exp)
        self.session.flush()

    def run(self):
        Experiment.run(self)
        instances = self.get_instances()
        with_density = instances.num_instances() < 150000
        if not with_density:
            self.exp_conf.logger.warning('There are more than 150.000, so '
                                         'the density plots are not '
                                         'displayed. ')
        stats = FeaturesAnalysis(instances, with_density=with_density)
        stats.gen_plots(self.output_dir())
        stats.gen_scoring(self.output_dir())

    def web_template(self):
        return 'features_analysis/main.html'


experiment.get_factory().register('FeaturesAnalysis',
                                  FeaturesAnalysisExperiment,
                                  FeaturesAnalysisConf)
