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

from secuml.core.active_learning.queries.categories \
        import Categories as CoreCategories
from secuml.core.classif.conf import classifiers
from secuml.core.classif.conf import ClassificationConf
from secuml.core.classif.conf.test.unlabeled_labeled \
        import UnlabeledLabeledConf
from secuml.exp.conf.features import FeaturesConf
from secuml.exp.diadem.conf.diadem import DiademConf
from secuml.exp.diadem import DiademExp

from .category import Category


class Categories(CoreCategories):

    def __init__(self, parent_exp, iteration, instances, assigned_categories,
                 assignment_proba, label, category_labels):
        CoreCategories.__init__(self, iteration, instances,
                                assigned_categories, assignment_proba, label,
                                category_labels)
        self.exp = parent_exp

    def init(self, label, families):
        self.categories = [Category(self.iteration, label, families[x])
                           for x in range(self.num_categories)]

    def get_naive_bayes_conf(self):
        name = '-'.join(['AL%d' % self.exp.exp_id,
                         'Iter%d' % self.iteration.iter_num,
                         'all',
                         'NaiveBayes'])
        classifier_conf = self.exp.exp_conf.core_conf.classifier_conf
        optim_conf = classifier_conf.hyperparam_conf.optim_conf
        multiclass = True
        factory = classifiers.get_factory()
        naive_bayes_conf = factory.get_default('GaussianNaiveBayes',
                                               optim_conf.num_folds,
                                               optim_conf.n_jobs, multiclass,
                                               self.exp.logger)
        test_conf = UnlabeledLabeledConf(self.exp.logger)
        classification_conf = ClassificationConf(naive_bayes_conf, test_conf,
                                                 self.exp.logger)
        features_conf = FeaturesConf(
                self.exp.exp_conf.features_conf.input_features,
                self.exp.exp_conf.features_conf.sparse,
                self.exp.exp_conf.features_conf.logger,
                filter_in_f=self.exp.exp_conf.features_conf.filter_in_f,
                filter_out_f=self.exp.exp_conf.features_conf.filter_out_f)
        exp_conf = DiademConf(self.exp.exp_conf.secuml_conf,
                              self.exp.exp_conf.dataset_conf,
                              features_conf,
                              self.exp.exp_conf.annotations_conf,
                              classification_conf, None, name=name,
                              parent=self.exp.exp_id)
        DiademExp(exp_conf, session=self.exp.session)
        return naive_bayes_conf
