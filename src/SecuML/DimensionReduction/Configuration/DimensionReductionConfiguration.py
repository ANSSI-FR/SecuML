## SecuML
## Copyright (C) 2016-2017  ANSSI
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

class DimensionReductionConfiguration(object):

    def __init__(self, algo):
        self.algo           = algo

    def generateSuffix(self):
        suffix  = '__' + self.algo.__name__
        return suffix

    def toJson(self):
        conf = {}
        conf['__type__'] = 'DimensionReductionConfiguration'
        return conf

    @staticmethod
    def generateParamsFromArgs(args):
        params = {}
        return params

    @staticmethod
    def generateParser(parser):
        return
