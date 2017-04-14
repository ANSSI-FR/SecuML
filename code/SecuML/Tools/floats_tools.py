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

import math
from scipy import stats

eps = 10e-10

def floatEquality(v1, v2):
    return math.fabs(v1 - v2) < eps

def log10_1(x):
    return math.log(1+x, 10)

def log10(x):
    return math.log(x, 10)

def harmonicMean(values):
    if 0 in values:
        return 0
    else:
        return stats.hmean(values)

def geometricMean(values):
    return stats.gmean(values)
