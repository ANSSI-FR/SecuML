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

from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod

from . import ClassifierConfFactory
from .ClassifierConf import ClassifierConf
from .test_conf import TestConfFactory
from .test_conf.TestConf import TestConf


class ClassificationConf(Conf):

    def __init__(self, classifier_conf, test_conf, logger):
        Conf.__init__(self, logger)
        self.classifier_conf = classifier_conf
        self.test_conf = test_conf

    def get_exp_name(self):
        name = ''
        if self.classifier_conf is not None:
            name += self.classifier_conf.get_exp_name()
        name += self.test_conf.get_exp_name()
        return name

    def fieldsToExport(self):
        return [('classifier_conf', exportFieldMethod.obj),
                ('test_conf', exportFieldMethod.obj)]

    @staticmethod
    def generateParser(parser):
        ClassifierConf.generateParser(parser)
        TestConf.generateParser(parser)

    @staticmethod
    def fromArgs(args, with_classifier_conf, logger):
        classifier_conf = None
        if with_classifier_conf:
            factory = ClassifierConfFactory.getFactory()
            classifier_conf = factory.fromArgs(args.model_class, args, logger)
        factory = TestConfFactory.getFactory()
        test_conf = factory.fromArgs(args.validation_mode, args, logger)
        return ClassificationConf(classifier_conf, test_conf, logger)

    def from_json(conf_json, logger):
        factory = ClassifierConfFactory.getFactory()
        classifier_conf = factory.from_json(conf_json['classifier_conf'],
                                            logger)
        factory = TestConfFactory.getFactory()
        test_conf = factory.from_json(conf_json['test_conf'], logger)
        return ClassificationConf(classifier_conf, test_conf, logger)
