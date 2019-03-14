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

from secuml.core.active_learning.strategies.rcd import Rcd
from secuml.core.classif.conf import ClassificationConf
from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod
from . import ActiveLearningConf


class RcdConf(ActiveLearningConf):

    def __init__(self, auto, budget, rcd_conf, multiclass_model_conf,
                 validation_conf, logger):
        ActiveLearningConf.__init__(self, auto, budget, multiclass_model_conf,
                                    validation_conf, logger)
        self.rcd_conf = rcd_conf

    @staticmethod
    def main_model_type():
        return 'multiclass'

    def _get_strategy(self):
        return Rcd

    def get_exp_name(self):
        return '%s__RCD_%s' % (ActiveLearningConf.get_exp_name(self),
                               self.rcd_conf.get_exp_name())

    def fields_to_export(self):
        fields = ActiveLearningConf.fields_to_export(self)
        fields.extend([('rcd_conf', exportFieldMethod.obj)])
        return fields

    @staticmethod
    def gen_parser(parser):
        al_group = ActiveLearningConf.gen_parser(parser, main_model=True)
        al_group.add_argument('--num-annotations',
                              type=int,
                              default=100,
                              help='Number of instances queried '
                                   'for each family.')
        al_group.add_argument('--cluster-strategy',
                              default='center_anomalous')

    @staticmethod
    def from_args(args, main_model_conf, validation_conf, logger):
        strategy = RcdStrategyConf(main_model_conf, args.cluster_strategy,
                                   args.num_annotations, 'uniform', logger)
        return RcdConf(args.auto, args.budget, strategy, main_model_conf,
                       validation_conf, logger)

    @staticmethod
    def from_json(obj, main_model_conf, validation_conf, logger):
        rcd_conf = RcdStrategyConf.from_json(obj['rcd_conf'], logger)
        return RcdConf(obj['auto'], obj['budget'], rcd_conf, main_model_conf,
                       validation_conf, logger)


class RcdStrategyConf(Conf):

    def __init__(self, classification_conf, cluster_strategy, num_annotations,
                 cluster_weights, logger):
        Conf.__init__(self, logger)
        self.classification_conf = classification_conf
        self.cluster_strategy = cluster_strategy
        self.num_annotations = num_annotations
        self.cluster_weights = cluster_weights

    def get_exp_name(self):
        return '%s__num_annotations_%d' % (
                                       self.classification_conf.get_exp_name(),
                                       self.num_annotations)

    def fields_to_export(self):
        return [('classification_conf', exportFieldMethod.obj),
                ('cluster_strategy', exportFieldMethod.primitive),
                ('num_annotations', exportFieldMethod.primitive),
                ('cluster_weights', exportFieldMethod.primitive)]

    @staticmethod
    def from_json(obj, logger):
        classif_conf = ClassificationConf.from_json(obj['classification_conf'],
                                                    logger)
        return RcdStrategyConf(classif_conf, obj['cluster_strategy'],
                               obj['num_annotations'], obj['cluster_weights'],
                               logger)
