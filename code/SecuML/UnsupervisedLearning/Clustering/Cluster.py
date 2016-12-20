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

from __future__ import division

import copy
import numpy as np
import pandas as pd
import random

from SecuML.Data import labels_tools

class Cluster(object):

    def __init__(self):
        self.instances_ids = []
        self.distances = []
        self.distortion = 0
        self.distortion_per_instance = 0
        self.label = None
        self.num_instances = 0
        self.clusters_sublabels_stats = {}

    def addInstance(self, instance_id, distance, label, sublabel):
        self.num_instances += 1
        self.instances_ids.append(instance_id)
        self.distances.append(distance)
        self.distortion += distance
        if label:
            label = 'malicious'
        else:
            label = 'benign'
        if sublabel is not None:
            key = label + '__' + sublabel
            if key not in self.clusters_sublabels_stats:
                self.clusters_sublabels_stats[key] = 0
            self.clusters_sublabels_stats[key] += 1

    def finalComputation(self, unknown_cluster_id):
        unknown_cluster_id = self.setClusterLabel(unknown_cluster_id)
        if self.num_instances != 0:
            self.computeDistortionPerInstance()
            self.sortInstances()
        return unknown_cluster_id

    def computeDistortionPerInstance(self):
        self.distortion_per_instance = self.distortion / self.num_instances

    # The list of instances in the cluster are sorted accoriding to their distance from the centroid
    def sortInstances(self):
        distances = pd.DataFrame(
                np.zeros((self.num_instances, 1)),
                index = map(str, self.instances_ids),
                columns = ['distance'])
        distances['distance'] = self.distances
        if pd.__version__ in ['0.13.0', '0.14.1']:
            distances.sort(['distance'], inplace = True)
        else:
            distances.sort_values(['distance'], inplace = True)
        self.instances_ids = map(int, distances.index.values.tolist())
        self.distances = distances.distance.tolist()

    def setClusterLabel(self, unknown_cluster_id):
        max_occurrences = 0
        for key, v in self.clusters_sublabels_stats.iteritems():
            if v > max_occurrences:
                max_occurrences = v
                self.label = key
        if self.label is None:
            self.label = 'unknown_' + str(unknown_cluster_id)
            return unknown_cluster_id + 1
        else:
            return unknown_cluster_id

    def getClusterLabel(self):
        return self.label

    # c: center
    # e: edge (does not return instances from the center)
    # r: random (does not return instances from the center and the edge)
    # An instance cannot be in two sets among c, e and r.
    def getClusterInstances(self, num_instances, rand = False, drop_instances = None):
        num_center = int(num_instances/2)
        num_edge = num_instances - num_center
        if rand:
            num_random = num_instances
        else:
            num_random = 0
        if drop_instances is None:
            instances = copy.deepcopy(self.instances_ids)
        else:
            instances = copy.deepcopy([x for x in self.instances_ids if x not in drop_instances])
        c_e_r = {}
        if len(instances) < num_center:
            c_e_r['c'] = instances
            c_e_r['e'] = []
            c_e_r['r'] = []
        else:
            c_e_r['c'] = instances[:num_center]
            instances = instances[num_center:]
            if len(instances) < num_edge:
                c_e_r['e'] = instances
                c_e_r['r'] = []
            else:
                c_e_r['e'] = instances[-num_edge:]
                instances = instances[:-num_edge]
                if len(instances) < num_random:
                    c_e_r['r'] = instances
                else:
                    c_e_r['r'] = random.sample(instances, num_random)
        return c_e_r
    
    def getClusterLabelsSublabels(self, cursor, label_experiment_id):
        labels_sublabel = labels_tools.getLabelsSublabels(cursor, label_experiment_id, self.instances_ids)
        return labels_sublabel
    
    def getClusterLabelSublabelIds(self, label, sublabel, cursor, experiment_label_id):
        if label == 'unknown' and \
                (sublabel is None or sublabel == 'unknown'):
            ids = labels_tools.getUnlabeledIds(cursor, experiment_label_id, 
                    instance_ids = self.instances_ids)
        else:
            ids = labels_tools.getLabelSublabelIds(cursor, 
                    experiment_label_id, label, sublabel, 
                    instance_ids = self.instances_ids)
        return ids

    ## Remove semi automatic labels
    ## Annotations are preserved
    def removeClusterLabel(self, num_results, cursor, experiment_label_id):
        for instance_id in self.instances_ids:
            if not labels_tools.hasAnnotation(cursor, instance_id, experiment_label_id):
                labels_tools.removeLabel(cursor, experiment_label_id, instance_id)

    def addClusterLabel(self, num_results, label, sublabel, cursor,
            experiment_label_id, label_iteration, label_method):
        for instance_id in self.instances_ids:
            labels_tools.addLabel(cursor, experiment_label_id, instance_id, label, sublabel,
                    label_iteration, label_method, False)

    def toJson(self, drop_instances = None):
        obj = {}
        if drop_instances is None:
            obj['instances_ids'] = self.instances_ids
            obj['distances']     = self.distances
        else:
            obj['instances_ids'] = []
            obj['distances']     = []
            for i in range(len(self.instances_ids)):
                instance_id = self.instances_ids[i]
                if instance_id in drop_instances:
                    continue
                else:
                    obj['instances_ids'].append(instance_id)
                    obj['distances'].append(self.distances[i])
        obj['label']                   = self.label
        obj['distortion']              = self.distortion
        obj['distortion_per_instance'] = self.distortion_per_instance
        obj['num_instances']           = len(obj['instances_ids'])
        return obj

    @staticmethod
    def fromJson(obj):
        cluster = Cluster()
        cluster.instances_ids           = obj['instances_ids']
        cluster.distances               = obj['distances']
        cluster.label                   = obj['label']
        cluster.distortion              = obj['distortion']
        cluster.distortion_per_instance = obj['distortion_per_instance']
        cluster.num_instances           = obj['num_instances']
        return cluster
