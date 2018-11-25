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

from SecuML.core.active_learning.strategies.queries.Categories \
        import Categories
from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf as CoreClassificationConf
from SecuML.core.classification.conf.GaussianNaiveBayesConf \
    import GaussianNaiveBayesConf
from SecuML.core.classification.conf.test_conf.UnlabeledLabeledConf \
        import UnlabeledLabeledConf
from SecuML.exp.classification.ClassificationConf \
        import ClassificationConf
from SecuML.exp.classification.ClassificationExperiment \
        import ClassificationExperiment

from .CategoryExp import CategoryExp


class CategoriesExp(Categories):

    def __init__(self, parent_exp, iteration, instances, assigned_categories,
                 assignment_proba, label, category_labels):
        Categories.__init__(self, iteration, instances, assigned_categories,
                            assignment_proba, label, category_labels)
        self.experiment = parent_exp

    def initCategories(self, label, families):
        self.categories = [CategoryExp(label, families[x])
                           for x in range(self.num_categories)]

    def getNaiveBayesConf(self):
        exp = self.experiment
        name = '-'.join(['AL%d' % exp.experiment_id,
                         'Iter%d' % self.iteration.iteration_number,
                         'all',
                         'NaiveBayes'])
        classifier_conf = exp.exp_conf.core_conf.classifier_conf
        naive_bayes_conf = GaussianNaiveBayesConf(False, True,
                                       classifier_conf.hyperparams_optim_conf,
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
        naive_bayes_exp = ClassificationExperiment(exp_conf,
                                                   session=exp.session)
        naive_bayes_exp.create_exp()
        return naive_bayes_conf
