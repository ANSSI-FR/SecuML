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

import logging
import numpy as np
import pandas as pd


def get_logger(name, level, output_file):
    logging.captureWarnings(True)
    level = logging.getLevelName(level)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if output_file is None:
        log_handler = logging.StreamHandler()
    else:
        log_handler = logging.FileHandler(output_file)
    logger.addHandler(log_handler)
    return logger, log_handler


def close_logger(logger, log_handler):
    logger.removeHandler(log_handler)
    log_handler.flush()
    log_handler.close()


def disable_matplotlib_logging():
    matplotlib_logger = logging.getLogger('matplotlib.font_manager')
    matplotlib_logger.setLevel(logging.CRITICAL)
    ch = logging.StreamHandler()
    matplotlib_logger.addHandler(ch)


def warnings_raise_errors():
    np.seterr(all='raise')
    pd.options.mode.chained_assignment = 'raise'
