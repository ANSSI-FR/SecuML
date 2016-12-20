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

import matplotlib.cm as cm
from matplotlib.colors import rgb2hex
import numpy as np

def colors(num):
    colors = cm.rainbow(np.linspace(0, 1, num))
    colors = map(rgb2hex, colors)
    return colors

def getLabelColor(label):
    color = 'blue'
    if label == 'malicious':
        color = 'red'
    elif label == 'benign':
        color = 'green'
    return color

