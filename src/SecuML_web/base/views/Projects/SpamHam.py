## SecuML
## Copyright (C) 2016-2017  ANSSI
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

from SecuML.config import INPUTDATA_DIR

def getInstance(experiment, view_id, instance_id, ident):
    dataset = experiment.dataset
    filename  = INPUTDATA_DIR + '/' + 'SpamHam' + '/'
    filename += dataset + '/raw_mail/' + ident
    with open(filename, 'r') as f:
        mail = f.read()
    return mail
