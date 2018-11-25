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


class ProjectionConf(Conf):

    def __init__(self, algo, logger):
        Conf.__init__(self, logger)
        self.algo = algo

    def get_exp_name(self):
        return self.algo.__name__

    def fieldsToExport(self):
        return [('algo', exportFieldMethod.obj_class)]

    @staticmethod
    def generateParser(parser):
        return
