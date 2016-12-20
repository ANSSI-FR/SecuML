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

import json

class BarPlot(object):

    def __init__(self, labels):
        self.barplot = {}
        self.barplot['labels'] = labels
        self.barplot['datasets'] = []

    def addDataset(self, data, fill_color, label):
        self.barplot['datasets'].append(
                {
                    'data': data,
                    'backgroundColor': fill_color,
                    'label': label
                    })

    def display(self, f):
            json.dump(self.barplot, f, indent = 2)

    def getJson(self):
        return json.dumps(self.barplot, indent = 2)
