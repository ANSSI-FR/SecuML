## SecuML
## Copyright (C) 2017  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

from SecuML.Classification.Configuration.GaussianNaiveBayesConfiguration \
        import GaussianNaiveBayesConfiguration
from SecuML.Classification.Configuration.TestConfiguration import TestConfiguration
from SecuML.Experiment.ClassificationExperiment import ClassificationExperiment

from Categories import Categories

class CategoriesExp(Categories):

    def __init__(self, parent_exp, iteration, instances, assigned_categories,
                 assignment_proba, label, category_labels):
        Categories.__init__(self, iteration, instances, assigned_categories, assignment_proba,
                            label, category_labels)
        self.experiment = parent_exp

    def getNaiveBayesConf(self):
        exp = self.experiment
        name = '-'.join(['AL' + str(exp.experiment_id),
                         'Iter' + str(self.iteration.iteration_number),
                         'all',
                         'NaiveBayes'])
        naive_bayes_exp = ClassificationExperiment(exp.project, exp.dataset, exp.session,
                                                   experiment_name = name,
                                                   labels_id = exp.labels_id,
                                                   parent = exp.experiment_id)
        naive_bayes_exp.setFeaturesFilenames(exp.features_filenames)
        test_conf = TestConfiguration()
        test_conf.setUnlabeled(labels_annotations = 'annotations')
        naive_bayes_conf = GaussianNaiveBayesConfiguration(
                exp.classification_conf.num_folds, False, True, test_conf)
        naive_bayes_exp.setClassifierConf(naive_bayes_conf)
        naive_bayes_exp.createExperiment()
        naive_bayes_exp.export()
        return naive_bayes_conf
