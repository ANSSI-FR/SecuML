## SecuML
## Copyright (C) 2017  ANSSI
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

from SecuML.Data import idents_tools
from SecuML.Data import labels_tools
from SecuML.Tools import dir_tools

class ExportInstances(object):

    def __init__(self, instances):
        self.instances = instances

    def exportSecuML(self, project, dataset, features_filename, session = None):
        dataset_dir, features_dir, init_labels_dir = dir_tools.createDataset(project, dataset)
        self.exportIdents(dataset_dir + 'idents.csv', session)
        self.exportFeatures(features_dir + features_filename)
        if self.instances.hasTrueLabels():
            self.exportLabels(init_labels_dir + 'true_labels.csv')

    def exportIdents(self, output_filename, session):
        idents = self.instances.idents
        ids = self.instances.ids
        if idents is None:
            ids = self.instances.getIds()
            idents = idents_tools.getAllIdents(session)
        with open(output_filename, 'w') as f:
            print >>f, 'instance_id,ident'
            for i in range(self.instances.numInstances()):
                instance_id = ids[i]
                print >>f, str(instance_id) + ','  + idents[str(instance_id)].encode('utf-8')

    def exportFeatures(self, output_filename):
        header = ['instance_id'] + [str(f) for f in self.instances.features_names]
        with open(output_filename, 'w') as f:
            print >>f, ','.join(header)
            for instance_id in self.instances.getIds():
                print >>f, str(instance_id) + ',' + ','.join(map(str, self.instances.getInstance(instance_id)))

    def exportLabels(self, output_filename):
        with open(output_filename, 'w') as f:
            print >>f, 'instance_id,label,family'
            for i in range(self.instances.numInstances()):
                instance_id = self.instances.ids[i]
                label = labels_tools.labelBooleanToString(self.instances.labels[i])
                family = self.instances.families[i]
                print >>f, str(instance_id) + ',' + str(label) + ',' + str(family)
