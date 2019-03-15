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

import copy


def extract_rows_with_thresholds(df, t_min, t_max, column_label,
                                 deepcopy=False):
    selected_df = df
    if t_min is not None:
        selection = selected_df.loc[:, column_label] > t_min
        selected_df = selected_df.loc[selection, :]
    if t_max is not None:
        selection = selected_df.loc[:, column_label] <= t_max
        selected_df = selected_df.loc[selection, :]
    if deepcopy:
        return copy.deepcopy(selected_df)
    else:
        return selected_df


def sort_data_frame(df, column, ascending, inplace):
    if inplace:
        df.sort_values([column], ascending=[ascending], inplace=inplace)
        return
    else:
        return df.sort_values([column], ascending=[ascending], inplace=inplace)
