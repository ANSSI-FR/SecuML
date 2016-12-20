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

    def __init__(self, num_components = None, sublabels_supervision = None):
        ProjectionConfiguration.__init__(self, num_components, sublabels_supervision = sublabels_supervision)

    def generateSuffix(self):
        suffix = ProjectionConfiguration.generateSuffix(self)
        if self.sublabels_supervision:
            suffix += '__sublabelsSupervision'
        return suffix

    def toJson(self):
        conf = ProjectionConfiguration.toJson(self)
        conf['__type__'] = 'SemiSupervisedProjectionConfiguration'
        return conf
