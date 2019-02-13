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

import numpy as np

from secuml.core.classif.classifiers.logistic_regression \
        import LogisticRegression
from secuml.core.conf import exportFieldMethod
from . import SupervisedClassifierConf


class LogisticRegressionConf(SupervisedClassifierConf):

    def __init__(self, multiclass, optim_algo, hyper_conf, logger):
        SupervisedClassifierConf.__init__(self, multiclass, hyper_conf, logger)
        self.optim_algo = optim_algo

    def _get_model_class(self):
        return LogisticRegression

    def get_exp_name(self):
        name = SupervisedClassifierConf.get_exp_name(self)
        name += '__%s' % self.optim_algo
        return name

    def fields_to_export(self):
        fields = SupervisedClassifierConf.fields_to_export(self)
        fields.append(('optim_algo', exportFieldMethod.primitive))
        return fields

    def is_probabilist(self):
        return True

    def get_feature_importance(self):
        if not self.multiclass:
            return 'weight'
        else:
            return None

    @staticmethod
    def _get_hyper_desc():
        hyper = {}
        hyper['regularization'] = {}
        hyper['regularization']['values'] = {
                                       'type': float,
                                       'default': list(10. ** np.arange(-2, 2))}
        hyper['regularization']['sklearn_name'] = 'C'
        hyper['penalty'] = {}
        hyper['penalty']['values'] = {'choices': ['l1', 'l2'],
                                      'default': ['l1', 'l2']}
        return hyper

    @staticmethod
    def gen_parser(parser):
        SupervisedClassifierConf.gen_parser(
                                  parser,
                                  LogisticRegressionConf._get_hyper_desc())
        parser.add_argument('--optim-algo',
                            choices=['sag', 'liblinear'],
                            default='liblinear',
                            help='sag is recommended for large datasets.'
                                 'Default: liblinear.')

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return LogisticRegressionConf(multiclass, obj['optim_algo'],
                                      hyperparam_conf,
                                      logger)

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        try:
            optim_algo = args.optim_algo
        except:
            optim_algo = 'liblinear'
        return LogisticRegressionConf(args.multiclass, optim_algo,
                                      hyperparam_conf, logger)
