# SecuML
# Copyright (C) 2017-2018  ANSSI
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

import csv
import os.path as path

from SecuML.core.Data import labels_tools

from SecuML.experiments.Data import idents_tools
from SecuML.experiments.Tools import dir_exp_tools


class ExportInstances(object):

    def __init__(self, instances):
        self.instances = instances

    def exportSecuML(self, project, dataset, features_filename, session=None):
        dataset_dir, features_dir, init_annotations_dir = dir_exp_tools.createDataset(
            project, dataset)
        self.exportIdents(path.join(dataset_dir, 'idents.csv'), session)
        self.exportFeatures(path.join(features_dir, features_filename))
        self.exportFeaturesNamesDescriptions(path.join(features_dir,
                                                       features_filename[:-4] + '_description.csv'))
        if self.instances.hasGroundTruth():
            self.exportLabels(path.join(init_annotations_dir, 'ground_truth.csv'))

    def exportIdents(self, output_filename, session):
        idents = self.instances.ids.idents
        ids = self.instances.ids.getIds()
        if idents is None:
            idents = idents_tools.getAllIdents(session)
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['instance_id', 'ident'])
            for i in range(self.instances.numInstances()):
                instance_id = ids[i]
                csv_writer.writerow([instance_id, idents[str(instance_id)]])

    def exportFeatures(self, output_filename):
        header  = ['instance_id']
        header += [f for f in range(self.instances.features.numFeatures())]
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            for instance_id in self.instances.ids.getIds():
                r  = [instance_id]
                r += self.instances.features.getInstanceFeatures(instance_id)
                csv_writer.writerow(r)

    def exportFeaturesNamesDescriptions(self, output_filename):
        header = ['id', 'name', 'description']
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            for i in range(self.instances.features.numFeatures()):
                row = [i,
                       self.instances.features.getNames()[i],
                       self.instances.features.getDescriptions()[i]]
                csv_writer.writerow(row)

    def exportLabels(self, output_filename):
        header = ['instance_id', 'label', 'family']
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            ids = self.instances.ids.getIds()
            for instance_id in ids:
                label = labels_tools.labelBooleanToString(
                    self.instances.annotations.getLabel(instance_id))
                family = self.instances.annotations.getFamily(instance_id)
                row = [instance_id, label, family]
                csv_writer.writerow(row)
