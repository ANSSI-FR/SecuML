# SecuML
# Copyright (C) 2017  ANSSI
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

from SecuML.core.ActiveLearning.QueryStrategies.AnnotationQueries.Categories \
        import Categories
from SecuML.core.Classification.Configuration.GaussianNaiveBayesConfiguration \
    import GaussianNaiveBayesConfiguration
from SecuML.core.Classification.Configuration.TestConfiguration.UnlabeledLabeledConf \
        import UnlabeledLabeledConf
from SecuML.experiments.Classification.ClassificationExperiment \
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
        naive_bayes_exp = ClassificationExperiment(exp.secuml_conf,
                                                   session=exp.session)
        naive_bayes_exp.initExperiment(exp.project, exp.dataset,
                                       experiment_name=name,
                                       parent=exp.experiment_id)
        test_conf = UnlabeledLabeledConf(logger=exp.logger)
        naive_bayes_conf = GaussianNaiveBayesConfiguration(
            exp.conf.n_jobs,
            exp.conf.num_folds, False, True, test_conf,
            logger=exp.logger)
        naive_bayes_exp.setConf(naive_bayes_conf, exp.features_filename,
                                annotations_id=exp.annotations_id)
        naive_bayes_exp.export()
        return naive_bayes_conf
