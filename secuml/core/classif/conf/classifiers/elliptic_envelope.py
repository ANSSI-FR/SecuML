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

from secuml.core.classif.classifiers.elliptic_envelope import EllipticEnvelope
from . import UnsupervisedClassifierConf


class EllipticEnvelopeConf(UnsupervisedClassifierConf):

    def _get_model_class(self):
        return EllipticEnvelope

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return EllipticEnvelopeConf(hyperparam_conf, logger)

    def is_probabilist(self):
        return False

    def get_feature_importance(self):
        return None

    @staticmethod
    def _get_hyper_desc():
        hyper = {}
        hyper['contamination'] = {}
        hyper['contamination']['values'] = {'type': float,
                                            'default': 0.1}
        return hyper

    @staticmethod
    def gen_parser(parser):
        UnsupervisedClassifierConf.gen_parser(
                                         parser,
                                         EllipticEnvelopeConf._get_hyper_desc())

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return EllipticEnvelopeConf(hyperparam_conf, logger)
