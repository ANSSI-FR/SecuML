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

from . import ActiveLearningConf

from secuml.core.active_learning.strategies.gornitz import Gornitz
from secuml.core.classif.conf import ClassificationConf
from secuml.core.classif.conf.hyperparam import HyperparamConf
from secuml.core.classif.conf.classifiers.sssvdd import SssvddConf
from secuml.core.classif.conf.test.unlabeled_labeled import UnlabeledLabeledConf
from secuml.core.conf import exportFieldMethod


class GornitzConf(ActiveLearningConf):

    def __init__(self, auto, budget, batch, validation_conf, logger):
        binary_model_conf = self._get_main_model_conf(validation_conf, logger)
        ActiveLearningConf.__init__(self, auto, budget, binary_model_conf,
                                    validation_conf, logger)
        self.batch = batch

    @staticmethod
    def main_model_type():
        return None

    def _get_strategy(self):
        return Gornitz

    def _get_main_model_conf(self, validation_conf, logger):
        hyperparam_conf = HyperparamConf.get_default(None, None, False, None,
                                                     logger)
        classifier_conf = SssvddConf(hyperparam_conf, logger)
        return ClassificationConf(classifier_conf,
                                  UnlabeledLabeledConf(logger, None), logger,
                                  validation_conf=validation_conf)

    def get_exp_name(self):
        name = ActiveLearningConf.get_exp_name(self)
        name += '__batch_%d' % self.batch
        return name

    def fields_to_export(self):
        fields = ActiveLearningConf.fields_to_export(self)
        fields.extend([('batch', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser(parser):
        al_group = ActiveLearningConf.gen_parser(parser)
        al_group.add_argument('--batch',
                              type=int,
                              default=100,
                              help='Number of annotations asked from the user '
                                   'at each iteration.')

    @staticmethod
    def from_args(args, binary_model_conf, validation_conf, logger):
        return GornitzConf(args.auto, args.budget, args.batch, validation_conf,
                           logger)

    @staticmethod
    def from_json(obj, binary_model_conf, validation_conf, logger):
        return GornitzConf(obj['auto'], obj['budget'], obj['batch'],
                           validation_conf, logger)
