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

from secuml.core.conf import exportFieldMethod
from secuml.core.tools.core_exceptions import SecuMLcoreException

from . import OneFoldTestConf


class InvalidValidationDatasets(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ValidationDatasetsConf(OneFoldTestConf):

    def __init__(self, logger, validation_datasets, streaming, stream_batch):
        OneFoldTestConf.__init__(self, logger)
        self.method = 'datasets'
        self.validation_datasets = validation_datasets
        self.streaming = streaming
        self.stream_batch = stream_batch

    def get_exp_name(self):
        name = '__Test_Datasets_%s' % ('_'.join(self.validation_datasets))
        if self.streaming:
            name += '__streaming_Batch_%i' % self.stream_batch
        name += OneFoldTestConf.get_exp_name(self)
        return name

    def fields_to_export(self):
        fields = OneFoldTestConf.fields_to_export(self)
        fields.extend([('validation_datasets', exportFieldMethod.primitive)])
        fields.extend([('streaming', exportFieldMethod.primitive)])
        fields.extend([('stream_batch', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--validation-datasets', default=None, nargs='+',
                            help='Name(s) of the validation dataset(s).')
        parser.add_argument('--streaming', default=False, action='store_true',
                            help='When specified, the validation datasets are '
                                 'processed as a stream. '
                                 'In this case, alerts analyses are not '
                                 'available. ')
        parser.add_argument('--stream-batch', default=1000, type=int,
                            help='Size of the streaming batches. '
                                 'Default: 1000.')

    @staticmethod
    def from_args(args, logger):
        if len(set(args.validation_datasets)) < len(args.validation_datasets):
            raise InvalidValidationDatasets(
                                '--validation-datasets contains duplicates.')
        return ValidationDatasetsConf(logger, args.validation_datasets,
                                      args.streaming, args.stream_batch)

    @staticmethod
    def from_json(obj, logger):
        return ValidationDatasetsConf(logger, obj['validation_datasets'],
                                      obj['streaming'], obj['stream_batch'])

    def _gen_train_test(self, classifier_conf, instances):
        return instances, None
