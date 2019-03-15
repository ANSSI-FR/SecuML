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

from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod


class Hyperparams(Conf):

    def __init__(self, logger):
        Conf.__init__(self, logger)
        self._hyper_values = set([])

    def add(self, name, hyper_values):
        setattr(self, name, hyper_values)
        self._hyper_values.add(name)

    def get_param_grid(self):
        return {'model__' + getattr(self, p).sklearn_name:
                getattr(self, p).values for p in self._hyper_values}

    def set_best_values(self, grid_search):
        best_params = grid_search.best_params_
        for p in self._hyper_values:
            param = getattr(self, p)
            param.set_best_value(best_params['model__' + param.sklearn_name])

    def get_best_values(self):
        return {'model__' + getattr(self, p).sklearn_name:
                getattr(self, p).best_value for p in self._hyper_values}

    def fields_to_export(self):
        return [(p, exportFieldMethod.obj) for p in self._hyper_values]

    def gen_parser(parser, hyperparam_desc, cv_optim, subgroup=True):
        if hyperparam_desc is None:
            return
        group = parser
        if subgroup:
            group = parser.add_argument_group('Hyperparameters')
        sklearn_mess = 'See the scikit-learn documentation.'
        for p, params in hyperparam_desc.items():
            if cv_optim:
                params['nargs'] = '+'
                params['help'] = '%s Default value: [%s].' % \
                    (sklearn_mess,
                     ', '.join(map(str, params['values']['default'])))
            else:
                params['nargs'] = 1
                params['help'] = '%s Default value: %s.' % \
                                 (sklearn_mess,
                                  str(params['values']['default']))
            p.replace('_', '-')
            group.add_argument('--%s' % p, help=params['help'],
                               nargs=params['nargs'], **params['values'])

    @staticmethod
    def from_args(args, hyperparam_desc, cv_optim, logger):
        if hyperparam_desc is None:
            return None
        hyper_values = Hyperparams(logger)
        for p, params in hyperparam_desc.items():
            hyper_values.add(p, HyperparamValues.from_args(args, p, params,
                                                           cv_optim, logger))
        return hyper_values

    @staticmethod
    def from_json(obj, hyperparam_desc, logger):
        if hyperparam_desc is None:
            return None
        hyper_values = Hyperparams(logger)
        for p in hyperparam_desc:
            hyper_values.add(p, HyperparamValues.from_json(obj[p], logger))
        return hyper_values

    @staticmethod
    def get_default(hyperparam_desc, logger):
        if hyperparam_desc is None:
            return None
        hyper_values = Hyperparams(logger)
        for p, params in hyperparam_desc.items():
            sklearn_name = p
            if 'sklearn_name' in params:
                sklearn_name = params['sklearn_name']
            hyper_values.add(p, HyperparamValues(params['values']['default'],
                                                 sklearn_name, logger))
        return hyper_values


class HyperparamValues(Conf):

    def __init__(self, values, sklearn_name, logger):
        Conf.__init__(self, logger)
        self.values = values
        self.sklearn_name = sklearn_name
        self.best_value = None

    def set_best_value(self, best_value):
        self.best_value = best_value

    @staticmethod
    def from_json(obj, logger):
        conf = HyperparamValues(obj['values'], obj['sklearn_name'], logger)
        conf.set_best_value(obj['best_value'])
        return conf

    @staticmethod
    def from_args(args, name, param, cv_optim, logger):
        sklearn_name = name
        if 'sklearn_name' in param:
            sklearn_name = param['sklearn_name']
        if name in vars(args):
            values = vars(args)[name]
        else:
            values = param['values']['default']
        if not cv_optim:
            values = [values]
        hyper_values = HyperparamValues(values, sklearn_name, logger)
        if not cv_optim:
            hyper_values.set_best_value(values[0])
        return hyper_values

    def fields_to_export(self):
        return [('values', exportFieldMethod.primitive),
                ('sklearn_name', exportFieldMethod.primitive),
                ('best_value', exportFieldMethod.primitive)]
