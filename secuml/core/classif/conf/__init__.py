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

from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod
from secuml.core.conf import register_submodules

from . import classifiers
from . import test
from .test import TestConf


class ClassificationConf(Conf):

    def __init__(self, classifier_conf, test_conf, logger,
                 validation_conf=None):
        Conf.__init__(self, logger)
        self.classifier_conf = classifier_conf
        self.test_conf = test_conf
        self.validation_conf = validation_conf

    def get_exp_name(self):
        name = ''
        if self.classifier_conf is not None:
            name += self.classifier_conf.get_exp_name()
        name += self.test_conf.get_exp_name()
        return name

    def fields_to_export(self):
        return [('classifier_conf', exportFieldMethod.obj),
                ('test_conf', exportFieldMethod.obj)]

    @staticmethod
    def gen_parser(parser):
        TestConf.gen_parser(parser)

    @staticmethod
    def from_args(args, logger):
        classifier_conf = classifiers.get_factory().from_args(args.model_class,
                                                              args, logger)
        test_conf = test.get_factory().from_args(args.validation_mode, args,
                                                 logger)
        return ClassificationConf(classifier_conf, test_conf, logger)

    def from_json(conf_json, logger):
        classifier_conf = classifiers.get_factory().from_json(
                                            conf_json['classifier_conf'],
                                            logger)
        test_conf = test.get_factory().from_json(conf_json['test_conf'],
                                                 logger)
        return ClassificationConf(classifier_conf, test_conf, logger)


register_submodules(classifiers, classifiers.get_factory())
register_submodules(test, test.get_factory())
