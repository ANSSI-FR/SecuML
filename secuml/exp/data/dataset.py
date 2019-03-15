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

from .annotations import Annotations
from .load_features import LoadFeatures
from .project_dataset import ProjectDataset


class Dataset(object):

    def __init__(self, exp_conf, session):
        self.session = session
        self.project_dataset = ProjectDataset(exp_conf.dataset_conf,
                                              exp_conf.secuml_conf, session)
        self.annotations = Annotations(exp_conf.dataset_conf,
                                       exp_conf.annotations_conf,
                                       exp_conf.secuml_conf, session)
        self.features = LoadFeatures(exp_conf, exp_conf.secuml_conf, session)

    def load(self):
        self.project_dataset.load()
        self.annotations.load()
        self.features.load()
