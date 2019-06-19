# SecuML
# Copyright (C) 2016-2019  ANSSI
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
import os
import os.path as path

from secuml.exp.data import idents_tools


def create_dataset(secuml_conf, project, dataset):
    dataset_dir = path.join(secuml_conf.input_data_dir, project, dataset)
    os.makedirs(dataset_dir)
    features_dir = path.join(dataset_dir, 'features')
    os.makedirs(features_dir)
    annotations_dir = path.join(dataset_dir, 'annotations')
    os.makedirs(annotations_dir)
    return dataset_dir, features_dir, annotations_dir


class ExportInstances(object):

    def __init__(self, instances, exp=None, user_instance_ids=False):
        self.instances = instances
        self.exp = exp
        self.ids = self.instances.ids.get_ids()
        self.user_instance_ids = None
        if user_instance_ids:
            self.user_instance_ids = idents_tools.get_all_user_instance_ids(
                    self.exp.session,
                    self.exp.exp_conf.dataset_conf.dataset_id)

    def export_to_secuml(self, secuml_conf, project, dataset,
                         features_filename):
        dataset_dir, features_dir, annotations_dir = create_dataset(
                                                                   secuml_conf,
                                                                   project,
                                                                   dataset)
        self.export_idents(path.join(dataset_dir, 'idents.csv'))
        self.export_features(path.join(features_dir, features_filename))
        description_filename = '_'.join([path.splitext(features_filename)[0],
                                         'description.csv'])
        self.export_features_names(path.join(features_dir,
                                             description_filename))
        if not self.instances.has_ground_truth():
            self.export_annotations(path.join(annotations_dir,
                                              'partial_annotations.csv'))

    def get_print_id(self, instance_id):
        print_id = instance_id
        if self.user_instance_ids is not None:
            print_id = self.user_instance_ids[str(instance_id)]
        return print_id

    def export_idents(self, output_filename):
        idents = self.instances.ids.idents
        if idents is None:
            idents = ['undefined'] * self.instances.num_instances()
        annotations = None
        has_ground_truth = self.instances.has_ground_truth()
        if has_ground_truth:
            annotations = self.instances.get_annotations(True)
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            header = ['instance_id', 'ident']
            if has_ground_truth:
                header.extend(['label', 'family'])
            csv_writer.writerow(header)
            for instance_id in self.ids:
                print_id = self.get_print_id(instance_id)
                values = [print_id, idents[str(instance_id)]]
                if has_ground_truth:
                    bool_label = annotations.get_label(instance_id)
                    family = annotations.get_family(instance_id)
                    values.extend([int(bool_label), family])
                csv_writer.writerow(values)

    def export_features(self, output_filename):
        header = ['instance_id']
        header.extend(range(self.instances.features.num_features()))
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            features = self.instances.features
            for instance_id in self.ids:
                print_id = self.get_print_id(instance_id)
                r = [print_id]
                r.extend(features.get_instance_features(instance_id))
                csv_writer.writerow(r)

    def export_features_names(self, output_filename):
        header = ['id', 'name', 'description']
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            for i in range(self.instances.features.num_features()):
                row = [i,
                       self.instances.features.get_names()[i],
                       self.instances.features.get_descriptions()[i]]
                csv_writer.writerow(row)

    def export_annotations(self, output_filename):
        header = ['instance_id', 'label', 'family']
        annotations = self.instances.get_annotations(False)
        with open(output_filename, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            for instance_id in self.ids:
                print_id = self.get_print_id(instance_id)
                bool_label = annotations.get_label(instance_id)
                family = annotations.get_family(instance_id)
                row = [print_id, int(bool_label), family]
                csv_writer.writerow(row)
