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
from SecuML.exp.conf.AnnotationsConf import AnnotationsConf
from SecuML.exp.conf.DatasetConf import DatasetConf
from SecuML.exp.conf.ExpConf import ExpConf
from SecuML.exp.conf.FeaturesConf import FeaturesConf
from SecuML.exp.Experiment import Experiment


class ValidationConf(ExpConf):

    @staticmethod
    def from_json(conf_json, secuml_conf):
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'],
                                             secuml_conf.logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               secuml_conf.logger)
        annotations_conf = AnnotationsConf.from_json(
                                                  conf_json['annotations_conf'],
                                                  secuml_conf.logger)
        exp_conf = ValidationConf(secuml_conf,
                                  dataset_conf,
                                  features_conf,
                                  annotations_conf,
                                  None,
                                  experiment_name=conf_json['experiment_name'],
                                  parent=conf_json['parent'])
        exp_conf.experiment_id = conf_json['experiment_id']
        return exp_conf

class ValidationExperiment(Experiment):
    pass


ExperimentFactory.getFactory().register('Validation',
                                        ValidationExperiment,
                                        ValidationConf)
