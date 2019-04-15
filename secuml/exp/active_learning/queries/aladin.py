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

from secuml.core.active_learning.queries.aladin \
        import AladinQueries as CoreAladinQueries
from secuml.core.classif.conf import classifiers
from secuml.core.classif.conf import ClassificationConf
from secuml.core.classif.conf.test.unlabeled_labeled \
        import UnlabeledLabeledConf

from secuml.exp.diadem.conf.diadem import DiademConf
from secuml.exp.diadem import DiademExp
from . import Query


class AladinQueries(CoreAladinQueries):

    def __init__(self, iteration, conf):
        CoreAladinQueries.__init__(self, iteration, conf)
        self.exp = self.iteration.exp

    def generate_query(self, instance_id, predicted_proba, suggested_label,
                       suggested_family, confidence=None):
        return Query(instance_id, predicted_proba, suggested_label,
                     suggested_family, confidence=confidence)

    def _create_naive_bayes_conf(self):
        name = '-'.join(['AL%d' % (self.exp.exp_id),
                         'Iter%d' % (self.iteration.iter_num),
                         'all',
                         'NaiveBayes'])
        multiclass_model = self.exp.exp_conf.core_conf.multiclass_model
        classifier_conf = multiclass_model.classifier_conf
        optim_conf = classifier_conf.hyperparam_conf.optim_conf
        multiclass = True
        factory = classifiers.get_factory()
        naive_bayes_conf = factory.get_default('GaussianNaiveBayes',
                                               optim_conf.num_folds,
                                               optim_conf.n_jobs, multiclass,
                                               self.exp.logger)
        test_conf = UnlabeledLabeledConf(self.exp.logger)
        classif_conf = ClassificationConf(naive_bayes_conf, test_conf,
                                          self.exp.logger)
        DiademConf(self.exp.exp_conf.secuml_conf,
                   self.exp.exp_conf.dataset_conf,
                   self.exp.exp_conf.features_conf,
                   self.exp.exp_conf.annotations_conf,
                   classif_conf, None, name=name, parent=self.exp.exp_id)
        return naive_bayes_conf

    def _run_logistic_regression(self):
        name = '-'.join(['AL%d' % (self.exp.exp_id),
                         'Iter%d' % (self.iteration.iter_num),
                         'all',
                         'LogisticRegression'])
        exp_conf = DiademConf(self.exp.exp_conf.secuml_conf,
                              self.exp.exp_conf.dataset_conf,
                              self.exp.exp_conf.features_conf,
                              self.exp.exp_conf.annotations_conf,
                              self.exp.exp_conf.core_conf.multiclass_model,
                              None, name=name, parent=self.exp.exp_id)
        model_exp = DiademExp(exp_conf, session=self.exp.session)
        model_exp.run(instances=self.iteration.datasets.instances,
                      cv_monitoring=False)
        train_exp = model_exp.get_train_exp()
        test_exp = model_exp.get_detection_exp('test')
        self.lr_predicted_proba = test_exp.predictions.all_probas
        self.lr_predicted_labels = test_exp.predictions.values
        self.lr_class_labels = train_exp.classifier.class_labels
        self.lr_time = train_exp.monitoring.exec_time
        self.lr_time += test_exp.monitoring.exec_time
