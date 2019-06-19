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

from secuml.core.tools.core_exceptions import SecuMLcoreException


# db_type: mysql or postgresql
def call_specific_db_func(db_type, function, args):
    if db_type == 'mysql':
        from . import mysql_specific
        module = mysql_specific
    elif db_type == 'postgresql':
        from . import postgresql_specific
        module = postgresql_specific
    else:
        assert(False)
    return getattr(module, function)(*args)


class InvalidIdentsFile(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class InvalidAnnotationsFile(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def idents_header_info(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        if header[0] != 'instance_id':
            raise InvalidIdentsFile('The field "instance_id" must be the '
                                    'first in idents.csv.')
        elif header[1] != 'ident':
            raise InvalidIdentsFile('The field "idents" must be the second in '
                                    'idents.csv.')
        fields = set(header)
        has_timestamp = False
        gt_label = False
        gt_families = False
        if 'timestamp' in fields:
            has_timestamp = True
        if 'label' in fields:
            gt_label = True
        if 'family' in fields:
            gt_families = True
        if not gt_label and gt_families:
            raise InvalidIdentsFile('The field "label" must be specified in '
                                    'idents.csv. You cannot specify only the '
                                    'families.')
        return has_timestamp, gt_label, gt_families


def annotations_with_families(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        num_fields = len(header)
        if num_fields >= 2:
            if header[0] != 'instance_id':
                raise InvalidAnnotationsFile('The field "instance_id" must be '
                                             'the first in the annotation '
                                             'file %s.' % (filename))
            if header[1] != 'label':
                raise InvalidAnnotationsFile('The field "label" must be the '
                                             'second in the annotation file '
                                             '%s.' % (filename))
            if num_fields == 3:
                if header[2] != 'family':
                    raise InvalidAnnotationsFile('Invalid field %s in the '
                                                 'annotation file %s.'
                                                 % (header[2], filename))
                return True
            elif num_fields == 2:
                return False
            elif num_fields > 3:
                raise InvalidAnnotationsFile('There are too many fields in '
                                             'the annotation file %s.'
                                             % (filename))
        else:
            raise InvalidAnnotationsFile('Some fields are missing from the '
                                         'annotation file %s. The fields '
                                         '"instance_id" and "label" are '
                                         'mandatory. The field "family" is '
                                         'optional.' % (filename))
