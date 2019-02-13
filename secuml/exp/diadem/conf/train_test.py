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

from secuml.core.classif.conf import classifiers
from secuml.core.conf import exportFieldMethod
from secuml.exp.conf.annotations import AnnotationsConf
from secuml.exp.conf.dataset import DatasetConf
from secuml.exp.conf.exp import ExpConf
from secuml.exp.conf.features import FeaturesConf


class TrainConf(ExpConf):

    def __init__(self, secuml_conf, dataset_conf, features_conf,
                 annotations_conf, core_conf, name=None, parent=None,
                 fold_id=None):
        ExpConf.__init__(self, secuml_conf, dataset_conf, features_conf,
                         annotations_conf, core_conf, name=name, parent=parent)
        self.fold_id = fold_id

    def fields_to_export(self):
        fields = ExpConf.fields_to_export(self)
        fields.extend([('fold_id', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def from_json(conf_json, secuml_conf):
        logger = secuml_conf.logger
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'], logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               logger)
        annotations_conf = AnnotationsConf.from_json(
                                                  conf_json['annotations_conf'],
                                                  logger)
        factory = classifiers.get_factory()
        core_conf = factory.from_json(conf_json['core_conf'], logger)
        exp_conf = TrainConf(secuml_conf, dataset_conf, features_conf,
                             annotations_conf, core_conf,
                             name=conf_json['name'], parent=conf_json['parent'],
                             fold_id=conf_json['fold_id'])
        exp_conf.exp_id = conf_json['exp_id']
        return exp_conf


class TestConf(ExpConf):

    def __init__(self, secuml_conf, dataset_conf, features_conf,
                 annotations_conf, classifier_conf, name=None, parent=None,
                 fold_id=None, kind='test'):
        ExpConf.__init__(self, secuml_conf, dataset_conf, features_conf,
                         annotations_conf, classifier_conf, name=name,
                         parent=parent)
        self.fold_id = fold_id
        self.kind = kind

    def fields_to_export(self):
        fields = ExpConf.fields_to_export(self)
        fields.extend([('fold_id', exportFieldMethod.primitive)])
        fields.extend([('kind', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def from_json(conf_json, secuml_conf):
        logger = secuml_conf.logger
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'], logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               logger)
        annotations_conf = AnnotationsConf.from_json(
                                                  conf_json['annotations_conf'],
                                                  logger)
        factory = classifiers.get_factory()
        classifier_conf = factory.from_json(conf_json['core_conf'], logger)
        exp_conf = TestConf(secuml_conf, dataset_conf, features_conf,
                            annotations_conf, classifier_conf,
                            name=conf_json['name'], parent=conf_json['parent'],
                            fold_id=conf_json['fold_id'],
                            kind=conf_json['kind'])
        exp_conf.exp_id = conf_json['exp_id']
        return exp_conf
