# SecuML
# Copyright (C) 2018  ANSSI
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

from . import ClassifierConfFactory
from .ClassifierConfiguration import ClassifierConfiguration


class AlreadyTrainedConfiguration(ClassifierConfiguration):

    def __init__(self):
        assert(False)

    def getModelClassName(self):
        assert(False)

    def generateSuffix(self):
        assert(False)

    @staticmethod
    def fromJson(obj, logger=None):
        assert(False)

    def toJson(self):
        assert(False)

    def probabilistModel(self):
        assert(False)

    def semiSupervisedModel(self):
        assert(False)

    @staticmethod
    def generateValidationParser(parser):
        parser.add_argument('--model-exp-id',
                            required=True,
                            type=int,
                            help='Id of the experiment that has trained the '
                                 'model.')
        validation_group = parser.add_argument_group('Validation parameters')
        validation_group.add_argument('--validation-dataset',
                                      required=True)

    @staticmethod
    def generateParser(parser):
        AlreadyTrainedConfiguration.generateValidationParser(parser)
        ClassifierConfiguration.generateAlertParser(parser)

    @staticmethod
    def generateParamsFromArgs(args, logger=None):
        params = ClassifierConfiguration.generateParamsFromArgs(args,
                                                                logger=logger)
        return params


ClassifierConfFactory.getFactory().registerClass('AlreadyTrainedConfiguration',
                                                 AlreadyTrainedConfiguration)
