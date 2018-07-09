# SecuML
# Copyright (C) 2018  ANSSI
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

import logging
#import numpy as np
import pandas as pd


def getDefaultConfig():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger


def disableMatplotlibLogging():
    matplotlib_logger = logging.getLogger('matplotlib.font_manager')
    matplotlib_logger.setLevel(logging.CRITICAL)


def warningsRaiseErrors():
    # np.seterr(all='raise')
    pd.options.mode.chained_assignment = "raise"
