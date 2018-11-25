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

import os.path as path

from SecuML.web import secuml_conf


def getInstance(experiment, view_id, user_instance_id, ident):
    dataset = experiment.exp_conf.dataset_conf.dataset
    directory = path.join(secuml_conf.input_data_dir,
                          'SpamHam',
                          dataset,
                          'raw_mail')
    with open(path.join(directory, ident), 'r') as f:
        mail = f.read()
    return mail
