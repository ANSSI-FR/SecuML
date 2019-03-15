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

from . import ObjectiveFuncConf


class AccuracyConf(ObjectiveFuncConf):

    def get_scoring_method(self):
        return 'accuracy'

    @staticmethod
    def gen_parser(parser):
        return

    @staticmethod
    def from_json(obj, logger):
        return AccuracyConf(logger)

    @staticmethod
    def from_args(args, logger):
        return AccuracyConf(logger)
