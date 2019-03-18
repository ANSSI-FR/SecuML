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

from secuml.core.classif.conf.classifiers import get_classifier_type
from secuml.core.classif.conf.classifiers import ClassifierType

from . import OneFoldTestConf


class UnlabeledLabeledConf(OneFoldTestConf):

    def __init__(self, logger, alerts_conf):
        OneFoldTestConf.__init__(self, logger, alerts_conf)
        self.method = 'unlabeled'

    def get_exp_name(self):
        name = '__UnlabeledLabeled'
        name += OneFoldTestConf.get_exp_name(self)
        return name

    @staticmethod
    def gen_parser(parser):
        return

    @staticmethod
    def from_args(args, logger):
        alerts_conf = OneFoldTestConf.alert_conf_from_args(args, logger)
        return UnlabeledLabeledConf(logger, alerts_conf)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = OneFoldTestConf.alert_conf_from_json(obj, logger)
        return UnlabeledLabeledConf(logger, alerts_conf)

    def _gen_train_test(self, classifier_conf, instances):
        classifier_type = get_classifier_type(classifier_conf.__class__)
        if classifier_type == ClassifierType.supervised:
            train_instances = instances.get_annotated_instances()
        else:
            train_instances = instances
        test_instances = instances.get_unlabeled_instances()
        return train_instances, test_instances
