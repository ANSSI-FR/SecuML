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

from secuml.core.classif.classifiers.lof import Lof
from secuml.core.conf import exportFieldMethod
from . import UnsupervisedClassifierConf


class LofConf(UnsupervisedClassifierConf):

    def __init__(self, n_jobs, hyper_conf, logger):
        UnsupervisedClassifierConf.__init__(self, hyper_conf, logger)
        self.n_jobs = n_jobs

    def _get_model_class(self):
        return Lof

    def fields_to_export(self):
        fields = UnsupervisedClassifierConf.fields_to_export(self)
        fields.append(('n_jobs', exportFieldMethod.primitive))
        return fields

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return LofConf(obj['n_jobs'], hyperparam_conf, logger)

    def is_probabilist(self):
        return False

    def get_feature_importance(self):
        return None

    @staticmethod
    def _get_hyper_desc():
        hyper = {}
        hyper['n_neighbors'] = {}
        hyper['n_neighbors']['values'] = {'type': int,
                                          'default': 20}
        hyper['algorithm'] = {}
        hyper['algorithm']['values'] = {'type': str,
                                        'choices': ['auto', 'ball_tree',
                                                    'kd_tree', 'brute'],
                                        'default': 'auto'}
        hyper['leaf_size'] = {}
        hyper['leaf_size']['values'] = {'type': int,
                                        'default': 30}
        hyper['metric'] = {}
        hyper['metric']['values'] = {'type': str,
                                     'choices': ['minkowski', 'cityblock',
                                                 'l1', 'l2', 'cosine',
                                                 'manhattan', 'euclidean'],
                                     'default': 'minkowski'}
        hyper['contamination'] = {}
        hyper['contamination']['values'] = {'type': float,
                                            'default': 0.1}
        return hyper

    @staticmethod
    def gen_parser(parser):
        UnsupervisedClassifierConf.gen_parser(parser,
                                              LofConf._get_hyper_desc())
        parser.add_argument('--n_jobs',
                            type=int,
                            default=-1,
                            help='Number of CPU cores used to train '
                                 'the isolation forest. '
                                 'If given a value of -1, all cores are used. '
                                 'Default: -1.')

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return LofConf(args.n_jobs, hyperparam_conf, logger)
