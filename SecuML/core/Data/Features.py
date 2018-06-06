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

import numpy as np


class InvalidFeatures(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Features(object):

    def __init__(self, values, names, descriptions, ids):
        self.ids = ids
        self.values = np.array(values)
        self.names = names
        self.descriptions = descriptions
        self.checkValidity()

    def checkValidity(self):
        message = None
        num_instances = self.ids.numInstances()

        if num_instances != 0:
            num_features = self.values.shape[1]
            if self.values.shape[0] != num_instances:
                message = 'There are ' + str(num_instances) + ' instances '
                message += 'but the features of ' + \
                    str(self.values.shape[0]) + ' instances are provided.'
            elif len(self.names) != num_features:
                message = 'There are ' + str(num_features) + ' features '
                message += 'but ' + str(len(self.names)) + \
                    ' features names are provided.'
            elif len(self.descriptions) != num_features:
                message = 'There are ' + str(num_features) + ' features '
                message += 'but ' + str(len(self.names)) + \
                    ' features names are provided.'
        else:
            if self.values.size != 0:
                message = 'There is 0 instance but some features are provided.'

        if message is not None:
            raise InvalidFeatures(message)

    def union(self, features):
        if features.getValues().shape[0] == 0:
            return
        if self.getValues().shape[0] == 0:
            self.values = features.values
        else:
            self.values = np.vstack((self.values, features.values))
        self.checkValidity()

    def getInstancesFromIds(self, instance_ids):
        extract = [self.getInstanceFeatures(i) for i in instance_ids]
        return extract

    def getNames(self):
        return self.names

    def getDescriptions(self):
        return self.descriptions

    def getValues(self):
        return self.values

    def numFeatures(self):
        return len(self.names)

    def getFeatureIndex(self, feature_name):
        return self.names.index(feature_name)

    def setInstanceFeatures(self, instance_id, features):
        index = self.ids.getIndex(instance_id)
        self.values[index] = features

    def getInstanceFeatures(self, instance_id):
        index = self.ids.getIndex(instance_id)
        return self.values[index]

    def getFeatureValues(self, feature_name):
        feature_index = self.getFeatureIndex(feature_name)
        return self.getFeatureValuesFromIndex(feature_index)

    def getFeatureValuesFromIndex(self, feature_index):
        return [self.values[i][feature_index] for i in range(self.ids.numInstances())]
