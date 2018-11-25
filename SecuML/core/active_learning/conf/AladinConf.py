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

from . import ActiveLearningConfFactory
from .ActiveLearningConf import ActiveLearningConf

from SecuML.core.active_learning.strategies.Aladin import Aladin
from SecuML.core.classification.conf.LogisticRegressionConf \
        import LogisticRegressionConf
from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf
from SecuML.core.classification.conf.hyperparam_conf.HyperparamOptimConf \
        import HyperparamOptimConf
from SecuML.core.classification.conf.hyperparam_conf.RocAucConf \
        import RocAucConf
from SecuML.core.classification.conf.test_conf.UnlabeledLabeledConf \
        import UnlabeledLabeledConf
from SecuML.core.Conf import exportFieldMethod


def aladinMulticlassModelConf(logger):
    hyperparams_optim_conf = HyperparamOptimConf(4, -1, RocAucConf(logger),
                                                 logger)
    classifier_conf = LogisticRegressionConf(False, True, 'liblinear',
                                             hyperparams_optim_conf, logger)
    return ClassificationConf(classifier_conf,
                              UnlabeledLabeledConf(logger, None),
                              logger)

def aladinBinaryModelConf(logger):
    hyperparams_optim_conf = HyperparamOptimConf(4, -1, RocAucConf(logger),
                                                 logger)
    classifier_conf = LogisticRegressionConf(False, False, 'liblinear',
                                             hyperparams_optim_conf, logger)
    return ClassificationConf(classifier_conf,
                              UnlabeledLabeledConf(logger, None),
                              logger)


class AladinConf(ActiveLearningConf):

    def __init__(self, auto, budget, num_annotations, validation_conf, logger):
        ActiveLearningConf.__init__(self, auto, budget, validation_conf,
                                    self.getModelsConf(logger), logger)
        self.query_strategy = 'Aladin'
        self.num_annotations = num_annotations

    def getModelsConf(self, logger):
        conf = {}
        conf['binary'] = aladinBinaryModelConf(logger)
        conf['multiclass'] = aladinMulticlassModelConf(logger)
        return conf

    def getStrategy(self, iteration):
        return Aladin(iteration)

    def get_exp_name(self):
        name = ActiveLearningConf.get_exp_name(self)
        name += '__batch_%d' %self.num_annotations
        return name

    @staticmethod
    def from_json(obj, logger):
        validation_conf = ActiveLearningConf.validation_conf_from_json(obj,
                                                                       logger)
        return AladinConf(obj['auto'], obj['budget'],obj['num_annotations'],
                          validation_conf, logger)

    def fieldsToExport(self):
        fields = ActiveLearningConf.fieldsToExport(self)
        fields.extend([('num_annotations', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConf.generateParser(parser)
        al_group.add_argument('--num-annotations',
                              type=int,
                              default=100,
                              help='Number of annotations asked from the user '
                                   'at each iteration.')

    @staticmethod
    def fromArgs(args, logger):
        validation_conf = ActiveLearningConf.validation_conf_from_args(args,
                                                                       logger)
        return AladinConf(args.auto, args.budget, args.num_annotations,
                          validation_conf, logger)


ActiveLearningConfFactory.getFactory().registerClass('AladinConf', AladinConf)
