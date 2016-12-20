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

class ProjectionConfiguration(object):

    def __init__(self, num_components = None, sublabels_supervision = None):
        self.num_components        = num_components
        self.sublabels_supervision = sublabels_supervision
        return
    
    def generateSuffix(self):
        suffix  = '__' + self.algo.__name__
        if self.num_components is not None:
            suffix += '__numComponents' + str(self.num_components)
        if self.sublabels_supervision:
            suffix += '__sublabelsSupervision'
        return suffix

    def toJson(self):
        conf = {}
        conf['__type__']              = 'ProjectionConfiguration'
        conf['num_components']        = self.num_components
        conf['sublabels_supervision'] = self.sublabels_supervision
        return conf
