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

import math
import sys


def float_equality(v1, v2):
    return math.fabs(v1 - v2) < sys.float_info.epsilon


def to_percentage(x):
    if math.isnan(x):
        return str(x)
    else:
        return '%.2f%%' % (x * 100)


def trunc(x):
    if math.isnan(x):
        return x
    else:
        return '%.2f' % (x)
