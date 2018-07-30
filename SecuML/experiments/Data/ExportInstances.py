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

    def __init__(self, instances, exp=None, user_instance_ids=False):
        self.instances = instances
        self.exp = exp
        self.ids = self.instances.ids.getIds()
        self.user_instance_ids = None
        if user_instance_ids:
            self.user_instance_ids = idents_tools.getAllUserInstanceIds(
                    self.exp.session,
                    self.exp.dataset_id)

    def exportSecuML(self, project, dataset, features_filename):
        dataset_dir, features_dir, annotations_dir = dir_exp_tools.createDataset(
            project, dataset)
        self.exportIdents(path.join(dataset_dir, 'idents.csv'))
        self.exportFeatures(path.join(features_dir, features_filename))
        description_filename = '_'.join([path.splitext(features_filename)[0],
                                         'description.csv'])
        self.exportFeaturesNamesDescriptions(path.join(features_dir,
                                                       description_filename))
        if self.instances.hasGroundTruth():
            self.exportAnnotations(path.join(annotations_dir,
                                             'ground_truth.csv'),
                                   ground_truth=True)
        else:
            self.exportAnnotations(path.join(annotations_dir,
                                             'partial_annotations.csv'),
                                   ground_truth=False)

    def getPrintId(self, instance_id):
        print_id = instance_id
        if self.user_instance_ids is not None:
            print_id = self.user_instance_ids[str(instance_id)]
        return print_id

    def exportIdents(self, output_filename):
        idents = self.instances.ids.idents
        if idents is None:
            idents = ['undefined'] * self.instances.numInstances()
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['instance_id', 'ident'])
            for instance_id in self.ids:
                print_id = self.getPrintId(instance_id)
                csv_writer.writerow([print_id, idents[str(instance_id)]])

    def exportFeatures(self, output_filename):
        header = ['instance_id']
        header.extend(range(self.instances.features.numFeatures()))
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            for instance_id in self.ids:
                print_id = self.getPrintId(instance_id)
                r  = [print_id]
                r.extend(self.instances.features.getInstanceFeatures(
                    instance_id))
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

    def exportAnnotations(self, output_filename, ground_truth=False):
        header = ['instance_id', 'label', 'family']
        annotations = self.instances.getAnnotations(ground_truth)
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            for instance_id in self.ids:
                print_id = self.getPrintId(instance_id)
                bool_label = annotations.getLabel(instance_id)
                label = labels_tools.labelBooleanToString(bool_label)
                family = annotations.getFamily(instance_id)
                row = [print_id, label, family]
                csv_writer.writerow(row)
