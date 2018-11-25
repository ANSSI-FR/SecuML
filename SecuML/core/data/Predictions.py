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

from . import Annotations
from SecuML.core.tools.core_exceptions import SecuMLcoreException


class InvalidPredictions(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Predictions(Annotations):

    def __init__(self, labels, families, predicted_proba, ids):
        Annotations.__init__(self, labels, families, ids)
        self.predicted_proba = predicted_proba
        self.checkValidity()

    def checkValidity(self):
        num_instances = self.ids.numInstances()
        if len(self.predicted_proba) != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d probabilities are provided.'
                                     % (num_instances,
                                        len(self.predicted_proba)))
