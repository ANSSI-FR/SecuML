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

from SecuML.core.active_learning.strategies.queries.AladinQueries \
        import AladinQueries
from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf as CoreClassificationConf
from SecuML.core.classification.conf.GaussianNaiveBayesConf \
        import GaussianNaiveBayesConf
from SecuML.core.classification.conf.test_conf.UnlabeledLabeledConf \
        import UnlabeledLabeledConf

from SecuML.exp.active_learning.strategies.queries.QueryExp \
        import QueryExp
from SecuML.exp.classification.ClassificationConf \
        import ClassificationConf



class AladinQueriesExp(AladinQueries):

    def __init__(self, iteration, conf):
        AladinQueries.__init__(self, iteration, conf)
        self.experiment = self.iteration.experiment

    def generateQuery(self, instance_id, predicted_proba,
                                suggested_label, suggested_family,
                                confidence=None):
        return QueryExp(instance_id, predicted_proba,
                                  suggested_label, suggested_family,
                                  confidence=confidence)

    def createNaiveBayesConf(self):
        exp = self.experiment
        name = '-'.join(['AL%d' % (exp.experiment_id),
                         'Iter%d' % (self.iteration.iteration_number),
                         'all',
                         'NaiveBayes'])
        models_conf = exp.exp_conf.core_conf.models_conf
        naive_bayes_conf = GaussianNaiveBayesConf(False, True,
            models_conf.multiclass.classifier_conf.hyperparams_optim_conf,
            exp.logger)
        test_conf = UnlabeledLabeledConf(exp.logger, None)
        classification_conf = CoreClassificationConf(naive_bayes_conf,
                                                     test_conf, exp.logger)
        exp_conf = ClassificationConf(exp.exp_conf.secuml_conf,
                                      exp.exp_conf.dataset_conf,
                                      exp.exp_conf.features_conf,
                                      exp.exp_conf.annotations_conf,
                                      classification_conf,
                                      experiment_name=name,
                                      parent=exp.experiment_id)
        return naive_bayes_conf
