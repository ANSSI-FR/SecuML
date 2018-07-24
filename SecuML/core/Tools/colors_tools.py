# SecuML
# Copyright (C) 2016  ANSSI
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

import matplotlib.cm as cm
from matplotlib.colors import rgb2hex
import numpy as np

from SecuML.core.Data import labels_tools

green = '#5cb85c'
red = '#d9534f'
blue = '#428bca'


def getLabelColor(label):
    global green
    global red
    global blue
    if label == labels_tools.MALICIOUS:
        return red
    elif label == labels_tools.BENIGN:
        return green
    elif label == 'all':
        return blue
    else:
        return None


def displayInRed(e):
    return '\033[91m {}\033[00m' .format(e)


def colors(num):
    colors = cm.rainbow(np.linspace(0, 1, num))
    colors = list(map(rgb2hex, colors))
    return colors
