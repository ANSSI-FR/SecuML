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

from SecuML.exp import ExperimentFactory
from SecuML.exp.Experiment import Experiment
from .ProjectionConf import ProjectionConf


class ProjectionExperiment(Experiment):

    def run(self, instances=None, export=True):
        Experiment.run(self)
        instances = self.getInstances()
        core_conf = self.exp_conf.core_conf
        dimension_reduction = core_conf.algo(core_conf)
        # Fit
        dimension_reduction.fit(instances)
        if export:
            dimension_reduction.exportFit(self.output_dir(), instances)
        # Transformation
        projected_instances = dimension_reduction.transform(instances)
        if export:
            dimension_reduction.exportTransform(self.output_dir(),
                                                instances, projected_instances)
        return projected_instances

    def webTemplate(self):
        return 'projection/main.html'


ExperimentFactory.getFactory().register('Projection',
                                        ProjectionExperiment,
                                        ProjectionConf)
