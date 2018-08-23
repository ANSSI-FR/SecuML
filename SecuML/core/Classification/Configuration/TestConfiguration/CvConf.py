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

from . import TestConfFactory
from .SeveralFoldsTestConfiguration import SeveralFoldsTestConfiguration


class CvConf(SeveralFoldsTestConfiguration):

    def __init__(self, num_folds, alerts_conf=None, logger=None):
        SeveralFoldsTestConfiguration.__init__(self, num_folds,
                                               alerts_conf=alerts_conf,
                                               logger=logger)
        self.method = 'cv'

    def generateSuffix(self):
        suffix = '__Test_Cv_' + str(self.num_folds)
        suffix += SeveralFoldsTestConfiguration.generateSuffix(self)
        return suffix

    @staticmethod
    def fromJson(obj, logger=None):
        alerts_conf = SeveralFoldsTestConfiguration.alertConfFromJson(
                                obj,
                                logger=logger)
        conf = CvConf(obj['num_folds'], alerts_conf, logger=logger)
        return conf

    def toJson(self):
        conf = SeveralFoldsTestConfiguration.toJson(self)
        conf['__type__'] = 'CvConf'
        return conf

    @staticmethod
    def generateParamsFromArgs(args, logger=None):
        params = SeveralFoldsTestConfiguration.generateParamsFromArgs(
                                    args,
                                    logger=logger)
        params['num_folds'] = args.num_folds
        return params


TestConfFactory.getFactory().registerClass('CvConf',
                                           CvConf)
