## SecuML
## Copyright (C) 2016  ANSSI
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

from SecuML.Experiment import ExperimentFactory
from SecuML.Experiment.Experiment import Experiment
from SecuML.Experiment import experiment_db_tools

from SecuML.ActiveLearning.Configuration.IlabConfiguration import IlabConfiguration
from SecuML.SupervisedLearning.Configuration import SupervisedLearningConfFactory
from SecuML.SupervisedLearning.Configuration.TestConfiguration import TestConfiguration

class ActiveLearningExperiment(Experiment):

    def __init__(self, project, dataset, db, cursor):
        Experiment.__init__(self, project, dataset, db, cursor)
        self.kind = 'ActiveLearning'
        self.labeling_method = None
    
    def setSupervisedLearningConf(self, supervised_learning_conf):
        self.supervised_learning_conf = supervised_learning_conf

    def setValidation(self, validation_dataset):
        self.validation_conf = None
        if validation_dataset is not None:
            self.validation_conf = TestConfiguration()
            self.validation_conf.setTestDataset(validation_dataset, self)
    
    def setRandomSamplingLabelChecking(self, batch):
        self.labeling_method = 'random_sampling'
        self.batch = batch

    def setClosestToBoundary(self, batch):
        self.labeling_method = 'closest_to_boundary'
        self.batch = batch

    def setILAB(self, ilab_conf):
        self.labeling_method = 'ILAB'
        self.ilab_conf = ilab_conf
        if ilab_conf.semiauto and ilab_conf.train_semiauto:
            self.supervised_learning_conf.setUnlabeled(labels_annotations = 'labels')

    def setCesaBianchi(self, b, batch):
        self.labeling_method = 'Cesa_Bianchi'
        self.b               = b
        self.batch           = batch

    def generateSuffix(self):
        suffix = ''
        suffix += self.supervised_learning_conf.generateSuffix()
        suffix += '__' + self.labeling_method
        if self.labeling_method == 'ILAB':
            suffix += self.ilab_conf.generateSuffix()
        if self.labeling_method in ['closest_to_boundary', 'random_sampling']:
            suffix += '__batch' + str(self.batch)
        if self.labeling_method == 'Cesa_Bianchi':
            suffix += '__b' + str(self.b)
        if self.validation_conf is not None:
            suffix += '__Validation' + self.validation_conf.test_dataset
            suffix += str(self.validation_conf.test_exp.experiment_id)
        return suffix
    
    def removeExperimentDB(self):
        super(ActiveLearningExperiment, self).removeExperimentDB()
        if self.experiment_id is not None:
            experiment_db_tools.removePredictedLabelsAnalysis(self.cursor, self.experiment_id)
        self.db.commit()

    @staticmethod
    def fromJson(obj, db, cursor):
        experiment = ActiveLearningExperiment(obj['project'], obj['dataset'], db, cursor)
        Experiment.expParamFromJson(experiment, obj)
        experiment.labeling_method  = obj['labeling_method']
        supervised_learning_conf = SupervisedLearningConfFactory.getFactory().fromJson(
                obj['supervised_learning_conf'], experiment)
        experiment.setSupervisedLearningConf(supervised_learning_conf)
        experiment.validation_conf = None
        if obj['validation_conf'] is not None:
            experiment.validation_conf = TestConfiguration.fromJson(obj['validation_conf'], experiment)
        if experiment.labeling_method == 'ILAB':
            experiment.ilab_conf = IlabConfiguration.fromJson(
                    obj['ilab_conf'])
        if experiment.labeling_method == 'Cesa_Bianchi':
            experiment.b = obj['b']
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ActiveLearningExperiment'
        conf['labeling_method'] = self.labeling_method
        conf['supervised_learning_conf'] = self.supervised_learning_conf.toJson()
        if self.validation_conf is not None:
            conf['validation_conf'] = self.validation_conf.toJson()
        else:
            conf['validation_conf'] = None
        if self.labeling_method == 'ILAB':
            conf['ilab_conf'] = self.ilab_conf.toJson()
        if self.labeling_method == 'Cesa_Bianchi':
            conf['b'] = self.b
        return conf
    
    def webTemplate(self):
        return 'ActiveLearning/active_learning.html'

ExperimentFactory.getFactory().registerClass('ActiveLearningExperiment', ActiveLearningExperiment)
