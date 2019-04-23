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

from . import OneFoldTestConf


class TestDatasetConf(OneFoldTestConf):

    def __init__(self, logger, test_dataset, streaming, stream_batch):
        OneFoldTestConf.__init__(self, logger)
        self.method = 'dataset'
        self.test_dataset = test_dataset
        self.streaming = streaming
        self.stream_batch = stream_batch

    def get_exp_name(self):
        name = '__Test_Dataset_' + self.test_dataset
        if self.streaming:
            name += '__streaming_Batch_%i' % self.stream_batch
        name += OneFoldTestConf.get_exp_name(self)
        return name

    def fields_to_export(self):
        fields = OneFoldTestConf.fields_to_export(self)
        fields.extend([('test_dataset', exportFieldMethod.primitive)])
        fields.extend([('streaming', exportFieldMethod.primitive)])
        fields.extend([('stream_batch', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--test-dataset', default=None,
                            help='Name of the test dataset.')
        parser.add_argument('--streaming', default=False, action='store_true',
                            help='When specify, the validation dataset is '
                                 'processed as a stream. '
                                 'In this case, alerts analyses are not '
                                 'available. ')
        parser.add_argument('--stream-batch', default=1000, type=int,
                            help='Size of the streaming batches. '
                                 'Default: 1000.')

    @staticmethod
    def from_args(args, logger):
        return TestDatasetConf(logger, args.test_dataset, args.streaming,
                               args.stream_batch)

    @staticmethod
    def from_json(obj, logger):
        return TestDatasetConf(logger, obj['test_dataset'], obj['streaming'],
                               obj['stream_batch'])

    def _gen_train_test(self, classifier_conf, instances):
        return instances, None
