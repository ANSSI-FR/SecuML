# SecuML
# Copyright (C) 2017-2018  ANSSI
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

from SecuML.core.ActiveLearning.QueryStrategies.AnnotationQueries.AladinAnnotationQueries import AladinAnnotationQueries
from SecuML.core.Classification.Configuration.GaussianNaiveBayesConfiguration import GaussianNaiveBayesConfiguration
from SecuML.core.Classification.Configuration.TestConfiguration.UnlabeledLabeledConf import UnlabeledLabeledConf

from SecuML.experiments.ActiveLearning.QueryStrategies.AnnotationQueries.AnnotationQueryExp import AnnotationQueryExp
from SecuML.experiments.Classification.ClassificationExperiment import ClassificationExperiment


class AladinAnnotationQueriesExp(AladinAnnotationQueries):

    def __init__(self, iteration, conf):
        AladinAnnotationQueries.__init__(self, iteration, conf)
        self.experiment = self.iteration.experiment

    def generateAnnotationQuery(self, instance_id, predicted_proba,
                                suggested_label, suggested_family, confidence=None):
        return AnnotationQueryExp(instance_id, predicted_proba,
                                  suggested_label, suggested_family, confidence=confidence)

    def createNaiveBayesConf(self):
        exp = self.experiment
        name = '-'.join(['AL' + str(exp.experiment_id),
                         'Iter' + str(self.iteration.iteration_number),
                         'all',
                         'NaiveBayes'])
        naive_bayes_exp = ClassificationExperiment(exp.project, exp.dataset, exp.session,
                                                   experiment_name=name,
                                                   parent=exp.experiment_id)
        test_conf = UnlabeledLabeledConf()
        naive_bayes_conf = GaussianNaiveBayesConfiguration(
            exp.conf.models_conf['multiclass'].num_folds,
            False, True, test_conf)
        naive_bayes_exp.setConf(naive_bayes_conf, exp.features_filename,
                                annotations_id=exp.annotations_id)
        naive_bayes_exp.export()
        return naive_bayes_conf
