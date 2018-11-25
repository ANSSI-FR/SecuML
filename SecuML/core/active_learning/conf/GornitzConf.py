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

from SecuML.core.active_learning.strategies.Gornitz import Gornitz
from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf
from SecuML.core.classification.conf.hyperparam_conf.HyperparamOptimConf \
        import HyperparamOptimConf
from SecuML.core.classification.conf.hyperparam_conf.RocAucConf \
        import RocAucConf
from SecuML.core.classification.conf.SssvddConf import SssvddConf
from SecuML.core.classification.conf.test_conf.UnlabeledLabeledConf \
        import UnlabeledLabeledConf
from SecuML.core.Conf import exportFieldMethod


class GornitzConf(ActiveLearningConf):

    def __init__(self, auto, budget, batch, validation_conf, logger):
        ActiveLearningConf.__init__(self, auto, budget, validation_conf,
                                    self.getModelsConf(logger),
                                    logger)
        self.query_strategy = 'Gornitz'
        self.batch = batch

    def getModelsConf(self, logger):
        conf = {}
        hyperparams_conf = HyperparamOptimConf(4, -1, RocAucConf(logger),
                                               logger)
        classifier_conf = SssvddConf(hyperparams_conf, logger)
        conf['binary'] = ClassificationConf(classifier_conf,
                                            UnlabeledLabeledConf(logger, None),
                                            logger)
        return conf

    def getStrategy(self, iteration):
        return Gornitz(iteration)

    def get_exp_name(self):
        name = ActiveLearningConf.get_exp_name(self)
        name += '__batch_%d' % self.batch
        return name

    def fieldsToExport(self):
        fields = ActiveLearningConf.fieldsToExport(self)
        fields.extend([('batch', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConf.generateParser(parser)
        al_group.add_argument('--batch',
                              type=int,
                              default=100,
                              help='Number of annotations asked from the user '
                                   'at each iteration.')

    @staticmethod
    def from_json(obj, logger):
        validation_conf = ActiveLearningConf.validation_conf_from_json(obj,
                                                                       logger)
        return GornitzConf(obj['auto'], obj['budget'], obj['batch'],
                           validation_conf, logger)

    @staticmethod
    def fromArgs(args, logger):
        validation_conf = ActiveLearningConf.validation_conf_from_args(args,
                                                                       logger)
        return GornitzConf(args.auto, args.budget, args.batch, validation_conf,
                           logger)


ActiveLearningConfFactory.getFactory().registerClass('GornitzConf', GornitzConf)
