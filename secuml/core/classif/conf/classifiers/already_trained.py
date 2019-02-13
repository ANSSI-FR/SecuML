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

from secuml.core.conf import exportFieldMethod

from . import ClassifierConf


class AlreadyTrainedConf(ClassifierConf):

    def __init__(self, model_exp_id, logger):
        ClassifierConf.__init__(self, None, None, logger)
        self.model_exp_id = model_exp_id

    def _get_model_class(self):
        return None

    def _set_model_class(self):
        self.model_class = None
        self.model_class_name = 'AlreadyTrained'

    def get_exp_name(self):
        return 'AlreadyTrained_exp%i' % self.model_exp_id

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return AlreadyTrainedConf(obj['model_exp_id'], logger)

    def fields_to_export(self):
        fields = ClassifierConf.fields_to_export(self)
        fields.extend([('model_exp_id', exportFieldMethod.primitive)])
        return fields

    def is_probabilist(self):
        return None

    @staticmethod
    def is_supervised():
        return None

    @staticmethod
    def _get_hyper_desc():
        return None

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--model-exp-id',
                            required=True,
                            type=int,
                            help='Id of the experiment that has trained the '
                                 'model.')

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return AlreadyTrainedConf(args.model_exp_id, logger)
