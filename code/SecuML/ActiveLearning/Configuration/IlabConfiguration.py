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

from SecuML.UnsupervisedLearning.Configuration import ClusteringConfFactory

class IlabConfiguration(object):

    def __init__(self, eps, stop_heterogeneous, train_semiauto, semiauto, num_unsure,
            clustering_conf):
        self.eps                = eps
        self.stop_heterogeneous = stop_heterogeneous
        self.train_semiauto     = train_semiauto
        self.semiauto           = semiauto
        self.num_unsure         = num_unsure
        self.clustering_conf    = clustering_conf

    def setFixedNumberAnnotations(self, num_malicious, num_benign, cluster_weights):
        self.num_malicious   = num_malicious
        self.num_benign      = num_benign
        self.cluster_weights = cluster_weights
        self.r               = None

    def setNumberAnnotations(self, r):
        self.r               = r
        self.num_malicious   = None 
        self.num_benign      = None 
        self.cluster_weights = None 

    def setClusteringConf(self, clustering_conf):
        self.clustering_conf = clustering_conf

    def generateSuffix(self):
        suffix = ''
        suffix += self.clustering_conf.generateSuffix()
        suffix += '__numUnsure' + str(self.num_unsure)
        if self.r is not None:
            suffix += '__r' + str(self.r)
        else:
            suffix += '__numAnnotations' + str(self.num_malicious + self.num_benign)
        if self.cluster_weights is not None:
            suffix += '__clusterWeights' + self.cluster_weights
        if self.stop_heterogeneous:
            suffix += 'stopHeterogeneous'
        if self.train_semiauto:
            suffix += '__trainSemiAuto'
        if self.semiauto:
            suffix += '_semiAuto'
        return suffix

    @staticmethod
    def fromJson(obj):
        clustering_conf = ClusteringConfFactory.getFactory().fromJson(obj['clustering_conf'])
        conf = IlabConfiguration(obj['eps'], obj['stop_heterogeneous'], obj['train_semiauto'], obj['semiauto'], 
                obj['num_unsure'], clustering_conf)
        if obj['r'] is not None:
            conf.setNumberAnnotations(obj['r'])
        else:
            conf.setFixedNumberAnnotations(obj['num_malicious'], obj['num_benign'],
                    obj['cluster_weights'])
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'IlabConfiguration'
        conf['eps']                = self.eps
        conf['stop_heterogeneous'] = self.stop_heterogeneous
        conf['train_semiauto']     = self.train_semiauto
        conf['semiauto']           = self.semiauto
        conf['clustering_conf']    = self.clustering_conf.toJson()
        conf['num_unsure']         = self.num_unsure
        conf['num_malicious']      = self.num_malicious
        conf['num_benign']         = self.num_benign
        conf['cluster_weights']    = self.cluster_weights
        conf['r']                  = self.r
        return conf
