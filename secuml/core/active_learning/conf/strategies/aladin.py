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

from . import ActiveLearningConf

from secuml.core.active_learning.strategies.aladin import Aladin
from secuml.core.classif.conf import classifiers
from secuml.core.classif.conf import ClassificationConf
from secuml.core.classif.conf.test.unlabeled_labeled \
        import UnlabeledLabeledConf
from secuml.core.conf import exportFieldMethod


class AladinConf(ActiveLearningConf):

    def __init__(self, auto, budget, num_annotations, validation_conf, logger):
        binary_model = self._get_lr_conf(validation_conf, logger)
        ActiveLearningConf.__init__(self, auto, budget, binary_model,
                                    validation_conf, logger)
        self.multiclass_model = self._get_lr_conf(None, logger,
                                                  multiclass=True)
        self.num_annotations = num_annotations

    def _get_lr_conf(self, validation_conf, logger, multiclass=False):
        factory = classifiers.get_factory()
        classifier_conf = factory.get_default('LogisticRegression',
                                              None, None, multiclass, logger)
        return ClassificationConf(classifier_conf,
                                  UnlabeledLabeledConf(logger), logger,
                                  validation_conf=validation_conf)

    @staticmethod
    def main_model_type():
        return None

    def _get_strategy(self):
        return Aladin

    def get_exp_name(self):
        return '%s__batch_%d' % (ActiveLearningConf.get_exp_name(self),
                                 self.num_annotations)

    def fields_to_export(self):
        fields = ActiveLearningConf.fields_to_export(self)
        fields.extend([('multiclass_model', exportFieldMethod.obj),
                       ('num_annotations', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser(parser):
        al_group = ActiveLearningConf.gen_parser(parser)
        al_group.add_argument('--num-annotations',
                              type=int,
                              default=100,
                              help='Number of annotations asked from the user '
                                   'at each iteration.')

    @staticmethod
    def from_args(args, binary_model_conf, validation_conf, logger):
        return AladinConf(args.auto, args.budget, args.num_annotations,
                          validation_conf, logger)

    @staticmethod
    def from_json(obj, binary_model_conf, validation_conf, logger):
        return AladinConf(obj['auto'], obj['budget'], obj['num_annotations'],
                          validation_conf, logger)
