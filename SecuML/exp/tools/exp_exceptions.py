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

class SecuMLexpException(Exception):
    pass


class UpdatedFile(SecuMLexpException):

    def __init__(self, filename, dataset):
        self.filename = filename
        self.dataset  = dataset

    def __str__(self):
        return('The file %s has been updated '
               'since the dataset %s has been loaded.'
               % (self.filename, self.dataset))


class UpdatedDirectory(SecuMLexpException):

    def __init__(self, directory, prev_files, new_files):
        self.directory = directory
        self.prev_files = prev_files
        self.new_files = new_files

    def __str__(self):
        return('The directory %s has been updated. \n'
               'Previous files: %s\n'
               'New files: %s.'
               % (self.directory,
                  ', '.join(self.prev_files),
                  ', '.join(self.new_files)))
