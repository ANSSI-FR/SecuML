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

active_learning_strategy_factory_exp = None


def getFactory():
    global active_learning_strategy_factory_exp
    if active_learning_strategy_factory_exp is None:
        active_learning_strategy_factory_exp = ActiveLearningStrategyFactoryExp()
    return active_learning_strategy_factory_exp


class ActiveLearningStrategyFactoryExp(object):

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def getStrategy(self, iteration, query_strategy):
        strategy = self.register[query_strategy + 'Exp'](iteration)
        return strategy
