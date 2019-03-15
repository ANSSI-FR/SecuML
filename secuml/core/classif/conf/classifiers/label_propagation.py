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

from secuml.core.classif.classifiers.label_propagation import LabelPropagation
from secuml.core.conf import exportFieldMethod
from . import SemiSupervisedClassifierConf


class LabelPropagationConf(SemiSupervisedClassifierConf):

    def __init__(self, multiclass, n_jobs, hyper_conf, logger):
        SemiSupervisedClassifierConf.__init__(self, multiclass, hyper_conf,
                                              logger)
        self.n_jobs = n_jobs

    def _get_model_class(self):
        return LabelPropagation

    def fields_to_export(self):
        fields = SemiSupervisedClassifierConf.fields_to_export(self)
        fields.append(('n_jobs', exportFieldMethod.primitive))
        return fields

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return LabelPropagationConf(multiclass, obj['n_jobs'], hyperparam_conf,
                                    logger)

    def is_probabilist(self):
        return True

    def get_feature_importance(self):
        return None

    @staticmethod
    def _get_hyper_desc():
        hyper = {}
        hyper['kernel'] = {}
        hyper['kernel']['values'] = {'type': str,
                                     'choices': ['rbf', 'knn'],
                                     'default': 'rbf'}
        hyper['n_neighbors'] = {}
        hyper['n_neighbors']['values'] = {'type': int,
                                          'default': 7}
        hyper['gamma'] = {}
        hyper['gamma']['values'] = {'type': float,
                                    'default': 20.0}
        return hyper

    @staticmethod
    def gen_parser(parser):
        SemiSupervisedClassifierConf.gen_parser(
                                        parser,
                                        LabelPropagationConf._get_hyper_desc())
        parser.add_argument('--n_jobs',
                            type=int,
                            default=-1,
                            help='Number of CPU cores used to train '
                                 'the isolation forest. '
                                 'If given a value of -1, all cores are used. '
                                 'Default: -1.')

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return LabelPropagationConf(args.multiclass, args.n_jobs,
                                    hyperparam_conf, logger)
