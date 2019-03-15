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

from secuml.core.classif.conf.alerts import AlertsConf
from secuml.core.classif.datasets import CvDatasets
from secuml.core.classif.datasets import Datasets
from secuml.core.conf import ConfFactory
from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod


test_conf_factory = None


def get_factory():
    global test_conf_factory
    if test_conf_factory is None:
        test_conf_factory = TestConfFactory()
    return test_conf_factory


class TestConfFactory(ConfFactory):
    pass


class TestConf(Conf):

    def __init__(self, logger, alerts_conf):
        Conf.__init__(self, logger)
        self.method = None
        self.alerts_conf = alerts_conf

    def get_exp_name(self):
        return ''

    @staticmethod
    def gen_parser(parser):
        methods = get_factory().get_methods()
        validation_group = parser.add_argument_group('Validation parameters')
        validation_group.add_argument(
                            '--validation-mode',
                            choices=methods,
                            default='RandomSplit',
                            help='Default: RandomSplit. '
                                 'TemporalSplit, CutoffTime, TemporalCv, and '
                                 'SlidingWindow require timestamped '
                                 'instances.')
        for method in methods:
            method_group = parser.add_argument_group(method + ' arguments')
            get_factory().gen_parser(method, method_group)
        AlertsConf.gen_parser(parser)

    @staticmethod
    def alert_conf_from_json(obj, logger):
        if obj['alerts_conf'] is None:
            return None
        return AlertsConf.from_json(obj['alerts_conf'], logger)

    @staticmethod
    def alert_conf_from_args(args, logger):
        return AlertsConf.from_args(args, logger)

    def fields_to_export(self):
        return [('method', exportFieldMethod.primitive),
                ('alerts_conf', exportFieldMethod.obj)]


class OneFoldTestConf(TestConf):

    def __init__(self, logger, alerts_conf):
        TestConf.__init__(self, logger, alerts_conf)

    def gen_datasets(self, classifier_conf, instances):
        train, test = self._gen_train_test(classifier_conf, instances)
        return Datasets(train, test)


class SeveralFoldsTestConf(TestConf):

    def __init__(self, logger, alerts_conf, num_folds):
        TestConf.__init__(self, logger, alerts_conf)
        self.num_folds = num_folds

    def fields_to_export(self):
        fields = TestConf.fields_to_export(self)
        fields.extend([('num_folds', exportFieldMethod.primitive)])
        return fields

    def gen_datasets(self, classifier_conf, instances, cv=None):
        if cv is not None:
            cv_split = cv
        else:
            cv_split = self._gen_cv_split(classifier_conf, instances)
        cv_datasets = CvDatasets()
        for fold_id, (train_ids, test_ids) in enumerate(cv_split):
            train_instances = instances.get_from_ids(train_ids)
            test_instances = instances.get_from_ids(test_ids)
            cv_datasets.add_dataset(Datasets(train_instances, test_instances))
        return cv_datasets
