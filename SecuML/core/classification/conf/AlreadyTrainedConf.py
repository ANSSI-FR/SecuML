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

from . import ClassifierConfFactory
from .ClassifierConf import ClassifierConf


class AlreadyTrainedConf(ClassifierConf):

    def __init__(self):
        assert(False)

    def get_exp_name(self):
        assert(False)

    @staticmethod
    def from_json(obj, logger):
        assert(False)

    def fieldsToExport(self):
        assert(False)

    def probabilistModel(self):
        assert(False)

    def semiSupervisedModel(self):
        assert(False)

    @staticmethod
    def generateParser(parser):
        ClassifierConf.generateParser(parser)
        parser.add_argument('--model-exp-id',
                            required=True,
                            type=int,
                            help='Id of the experiment that has trained the '
                                 'model.')


ClassifierConfFactory.getFactory().registerClass('AlreadyTrainedConf',
                                                 AlreadyTrainedConf)
