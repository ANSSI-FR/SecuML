# SecuML
# Copyright (C) 2017  ANSSI
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

from SecuML.core.Data import labels_tools

from SecuML.experiments.Data import idents_tools
from SecuML.experiments.Tools import dir_exp_tools


class ExportInstances(object):

    def __init__(self, instances):
        self.instances = instances

    def exportSecuML(self, project, dataset, features_filename, session=None):
        dataset_dir, features_dir, init_annotations_dir = dir_exp_tools.createDataset(
            project, dataset)
        self.exportIdents(dataset_dir + 'idents.csv', session)
        self.exportFeatures(features_dir + features_filename)
        self.exportFeaturesNamesDescriptions(
            features_dir + features_filename[:-4] + '_description.csv')
        if self.instances.hasGroundTruth():
            self.exportLabels(init_annotations_dir + 'ground_truth.csv')

    def exportIdents(self, output_filename, session):
        idents = self.instances.idents
        ids = self.instances.ids.getIds()
        if idents is None:
            idents = idents_tools.getAllIdents(session)
        with open(output_filename, 'w') as f:
            f.write('instance_id,ident' + '\n')
            for i in range(self.instances.numInstances()):
                instance_id = ids[i]
                f.write(str(instance_id) + ',' +
                        idents[str(instance_id)] + '\n')

    def exportFeatures(self, output_filename):
        header = ['instance_id'] + \
            [str(f) for f in range(self.instances.features.numFeatures())]
        with open(output_filename, 'w') as f:
            f.write(','.join(['"' + h + '"' for h in header]) + '\n')
            for instance_id in self.instances.ids.getIds():
                f.write(str(instance_id) + ',' + ','.join(map(str,
                                                              self.instances.features.getInstanceFeatures(instance_id))) + '\n')

    def exportFeaturesNamesDescriptions(self, output_filename):
        header = ['id', 'name', 'description']
        with open(output_filename, 'w') as f:
            f.write(','.join(header) + '\n')
            for i in range(self.instances.features.numFeatures()):
                row = [str(i),
                       '"' + self.instances.features.getNames()[i] + '"',
                       '"' + self.instances.features.getDescriptions()[i] + '"']
                f.write(','.join(row) + '\n')

    def exportLabels(self, output_filename):
        with open(output_filename, 'w') as f:
            f.write('instance_id,label,family' + '\n')
            ids = self.instances.ids.getIds()
            for instance_id in ids:
                label = labels_tools.labelBooleanToString(
                    self.instances.annotations.getLabel(instance_id))
                family = self.instances.annotations.getFamily(instance_id)
                f.write(str(instance_id) + ',' +
                        str(label) + ',' + str(family) + '\n')
