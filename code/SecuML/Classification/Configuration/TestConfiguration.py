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

from SecuML.Data.Dataset import Dataset
from SecuML.Experiment import ExperimentFactory
from SecuML.Experiment.ValidationExperiment import ValidationExperiment
from SecuML.Tools import mysql_tools

from AlertsConfiguration import AlertsConfiguration

class TestConfiguration(object):

    def __init__(self, alerts_conf = None):
        self.method = None
        self.test_exp = None
        self.alerts_conf = alerts_conf

    def setTestDataset(self, test_dataset, exp):
        self.method = 'test_dataset'
        self.test_dataset = test_dataset
        self.createTestExperiment(exp)

    def setRandomSplit(self, test_size):
        self.method = 'random_split'
        self.test_size = test_size

    def setUnlabeled(self, labels_annotations = 'labels'):
        self.method = 'unlabeled'
        self.labels_annotations = labels_annotations

    def createTestExperiment(self, exp):
        db, cursor = mysql_tools.getDbConnection()
        if not mysql_tools.databaseExists(cursor, exp.project, self.test_dataset):
            load_dataset = Dataset(exp.project, self.test_dataset,
                    db, cursor)
            load_dataset.load()
        ## Check if the validation experiments already exists
        self.test_exp = ValidationExperiment(
                exp.project, self.test_dataset,
                db, cursor)
        self.test_exp.setFeaturesFilenames(exp.features_filenames)
        self.test_exp.initLabels('true_labels.csv', overwrite = False)
        self.test_exp.export()

    def generateSuffix(self):
        if self.method == 'test_dataset':
            suffix = '__Test_' + self.test_dataset
        elif self.method == 'random_split':
            suffix = '__Test' + str(int(self.test_size * 100))
        elif self.method == 'unlabeled':
            suffix = '__UnlabeledLabeled'
        if self.alerts_conf is not None:
            suffix += self.alerts_conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, exp):
        alerts_conf = None
        if obj['alerts_conf'] is not None:
            alerts_conf = AlertsConfiguration.fromJson(
                    obj['alerts_conf'])
        conf = TestConfiguration(alerts_conf = alerts_conf)
        conf.method = obj['method']
        if obj['method'] == 'random_split':
            conf.setRandomSplit(obj['test_size'])
        elif obj['method'] == 'unlabeled':
            conf.setUnlabeled(obj['labels_annotations'])
        elif obj['method'] == 'test_dataset':
            conf.setTestDataset(obj['test_dataset'], exp)
            db, cursor = mysql_tools.getDbConnection()
            experiment_id = obj['test_exp']['experiment_id']
            conf.test_exp = ExperimentFactory.getFactory().fromJson(
                    exp.project, conf.test_dataset,
                    experiment_id, db, cursor)
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'TestConfiguration'
        conf['method'] = self.method
        conf['test_exp'] = None
        if self.method == 'test_dataset':
            conf['test_exp'] = self.test_exp.toJson()
            conf['test_dataset'] = self.test_dataset
        elif self.method == 'random_split':
            conf['test_size'] = self.test_size
        elif self.method == 'unlabeled':
            conf['labels_annotations'] = self.labels_annotations
        conf['alerts_conf'] = None
        if self.alerts_conf is not None:
            conf['alerts_conf'] = self.alerts_conf.toJson()
        return conf
