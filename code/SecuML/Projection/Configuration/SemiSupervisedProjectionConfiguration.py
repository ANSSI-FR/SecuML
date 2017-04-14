## SecuML
## Copyright (C) 2016  ANSSI
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

from ProjectionConfiguration import ProjectionConfiguration

class SemiSupervisedProjectionConfiguration(ProjectionConfiguration):

    def __init__(self, algo, num_components = None, families_supervision = None):
        ProjectionConfiguration.__init__(self, algo, num_components = num_components)
        self.families_supervision = families_supervision

    def generateSuffix(self):
        suffix = ProjectionConfiguration.generateSuffix(self)
        if self.families_supervision:
            suffix += '__familiesSupervision'
        return suffix

    def toJson(self):
        conf = ProjectionConfiguration.toJson(self)
        conf['__type__'] = 'SemiSupervisedProjectionConfiguration'
        conf['families_supervision'] = self.families_supervision
        return conf
