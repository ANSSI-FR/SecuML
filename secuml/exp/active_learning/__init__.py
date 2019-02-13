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

import importlib
import pkgutil


from secuml.exp.active_learning import strategies
for _, name, _ in pkgutil.iter_modules(strategies.__path__):
    class_name = ''.join(map(lambda x: x.capitalize(), name.split('_')))
    submodule = importlib.import_module(strategies.__name__ + '.' + name)
    strategies.get_factory().register(class_name, getattr(submodule,
                                                          class_name))
