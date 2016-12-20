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

from SecuML.Tools import colors_tools
from SecuML.Data.Tools.Features.CategoricalFeature import CategoricalFeature
from SecuML.Data.Tools.Stats.CategoricalStats import CategoricalStats

class PieStats(object):
    
    def __init__(self):
        self.stats = CategoricalStats()

    def add(self, key, value):
        self.stats.add(key, value)

    def addCategoricalFeature(self, categorical_feature):
        for key in categorical_feature.getKeys():
            self.stats.add(key, categorical_feature.getCount(key))

    def addCategoricalFeatureSeveralItems(self, categorical_feature_several_items, item):
        for key in categorical_feature_several_items.getKeys():
            self.stats.add(key, categorical_feature_several_items.getCount(key, item))

    def toCSV(self, output_file):
        with open(output_file + '.csv', 'w') as f:
            ## the header
            print >>f, 'key,count,prop'
            ## the values
            for key in self.stats.getKeys():
                output  = str(key) + ',' + str(self.stats.getCount(key))
                output += ',' + str(self.stats.getProp(key))
                print >>f, output
    
    def toJSON(self, output_file):
        num_colors = self.stats.numSelectedKeys()
        all_colors = colors_tools.colors(num_colors)
        with open(output_file + '.json', 'w') as f:
            ## the header
            print >>f, '['
            ## the values
            i = 0
            for key in self.stats.getKeys():
                if i != 0:
                    print >>f, ','
                string  = '{'
                string += '\t"label": "' + str(key) + '", '
                string += '\t"value": '  + str(self.stats.getCount(key)) + ','
                string += '\t"color": "' +  all_colors[i] + '"'
                string += '}'
                print >>f, string
                i += 1
            print >>f, ']'
    
    def display(self, output_file, thresholds_output, filtering = True):
        var_name = output_file.split('/')[-1]
        self.stats.finalComputations(var_name, [0.0001, 0.001, 0.01, 0.1], thresholds_output, filtering)
        self.toCSV(output_file)
        self.toJSON(output_file)
