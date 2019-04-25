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

from secuml.core.active_learning.strategies.ilab import Ilab
from secuml.core.classif.conf import classifiers
from secuml.core.classif.conf import ClassificationConf
from secuml.core.classif.conf.test.unlabeled_labeled \
        import UnlabeledLabeledConf
from secuml.core.conf import exportFieldMethod

from . import ActiveLearningConf
from .rcd import RcdStrategyConf


def _rcd_conf(args, logger):
    factory = classifiers.get_factory()
    classifier_conf = factory.get_default('LogisticRegression', None, None,
                                          True, logger)
    classif_conf = ClassificationConf(classifier_conf,
                                      UnlabeledLabeledConf(logger, None),
                                      logger)
    return RcdStrategyConf(classif_conf, args.cluster_strategy,
                           args.num_annotations, 'uniform', logger)


class IlabConf(ActiveLearningConf):

    def __init__(self, auto, budget, rcd_conf, num_uncertain,
                 binary_model_conf, validation_conf, logger):
        ActiveLearningConf.__init__(self, auto, budget, binary_model_conf,
                                    validation_conf, logger)
        self.num_uncertain = num_uncertain
        self.rcd_conf = rcd_conf

    @staticmethod
    def main_model_type():
        return 'binary'

    def _get_strategy(self):
        return Ilab

    def get_exp_name(self):
        name = ActiveLearningConf.get_exp_name(self)
        name += '__RCD_%s' % self.rcd_conf.get_exp_name()
        name += '__numUnsure_%d' % self.num_uncertain
        return name

    def fields_to_export(self):
        fields = ActiveLearningConf.fields_to_export(self)
        fields.extend([('num_uncertain', exportFieldMethod.primitive),
                       ('rcd_conf', exportFieldMethod.obj)])
        return fields

    @staticmethod
    def gen_parser(parser):
        al_group = ActiveLearningConf.gen_parser(parser, main_model=True)
        al_group.add_argument('--num-uncertain',
                              type=int,
                              default=10,
                              help='Number of instances queried close to the '
                                   'decision boundary.')
        al_group.add_argument('--num-annotations',
                              type=int,
                              default=45,
                              help='Number of instances queried for each '
                                   'family.')
        al_group.add_argument('--cluster-strategy',
                              default='center_anomalous')

    @staticmethod
    def from_args(args, binary_model_conf, validation_conf, logger):
        rcd_conf = _rcd_conf(args, logger)
        return IlabConf(args.auto, args.budget, rcd_conf, args.num_uncertain,
                        binary_model_conf, validation_conf, logger)

    @staticmethod
    def from_json(obj, binary_model_conf, validation_conf, logger):
        rcd_conf = RcdStrategyConf.from_json(obj['rcd_conf'], logger)
        return IlabConf(obj['auto'], obj['budget'], rcd_conf,
                        obj['num_uncertain'], binary_model_conf,
                        validation_conf, logger)
