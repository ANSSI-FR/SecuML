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

from . import ActiveLearningConf

from secuml.core.active_learning.strategies.cesa_bianchi import CesaBianchi
from secuml.core.conf import exportFieldMethod


class CesaBianchiConf(ActiveLearningConf):

    def __init__(self, auto, budget, batch, b, binary_model_conf,
                 validation_conf, logger):
        ActiveLearningConf.__init__(self, auto, budget, binary_model_conf,
                                    validation_conf, logger)
        self.b = b
        self.batch = batch

    @staticmethod
    def main_model_type():
        return 'binary'

    def _get_strategy(self):
        return CesaBianchi

    def get_exp_name(self):
        name = ActiveLearningConf.get_exp_name(self)
        name += '__b_%.2f' % self.b
        name += '__batch_%d' % self.batch
        return name

    def fields_to_export(self):
        fields = ActiveLearningConf.fields_to_export(self)
        fields.extend([('b', exportFieldMethod.primitive),
                       ('batch', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser(parser):
        al_group = ActiveLearningConf.gen_parser(parser, main_model=True)
        al_group.add_argument('--batch',
                              type=int,
                              default=100,
                              help='Number of annotations asked from the user '
                                   'at each iteration.')
        al_group.add_argument('--b',
                              type=float,
                              default=0.1)

    @staticmethod
    def from_args(args, binary_model_conf, validation_conf, logger):
        return CesaBianchiConf(args.auto, args.budget, args.batch, args.b,
                               binary_model_conf, validation_conf, logger)

    @staticmethod
    def from_json(obj, binary_conf, validation_conf, logger):
        return CesaBianchiConf(obj['auto'], obj['budget'], obj['batch'],
                               obj['b'], binary_conf, validation_conf, logger)
