## SecuML
## Copyright (C) 2016  ANSSI
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

import json
import math
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity
import sys

from SecuML.Tools import floats_tools

class NoDensity(Exception):
    def __str__(self):
        return 'NoDensity'

class DensityPlot(object):
   
    def __init__(self):
        self.data = []
        
    def add(self, value):
        self.data.append(value)

    def computeStats(self):
        self.output_stats['count']  = len(self.data)
        if self.output_stats['count'] == 0:
            self.output_stats['min']    = None 
            self.output_stats['max']    = None 
            self.output_stats['mean']   = None 
            self.output_stats['median'] = None 
            self.output_stats['var']    = None 
        else:
            self.output_stats['min']    = np.amin(self.data_np)
            self.output_stats['max']    = np.amax(self.data_np)
            self.output_stats['mean']   = np.mean(self.data_np)
            self.output_stats['median'] = np.percentile(self.data_np, 0.5)
            self.output_stats['var']    = np.var(self.data_np)

    def computeDensity(self, num_points, bandwidth):
        ## Transforms the input data into a matrix
        density_data = [[x] for x in  self.data_np]
        ## Computes the x axis
        delta = self.output_stats['max'] - self.output_stats['min']
        density_delta = 1.1 * delta
        x = np.arange(
            self.output_stats['min'] - 0.05*delta,
            self.output_stats['max'] + 0.05*delta,
            density_delta / num_points
            )
        x_density = [[y] for y in x]
        ## Computes the density
        kde = KernelDensity(kernel = 'gaussian', bandwidth = bandwidth)
        kde.fit(density_data)
        ## kde.score_samples returns the 'log' of the density
        y_log_density = kde.score_samples(x_density).tolist()
        y_density = map(math.exp, y_log_density)
        ## Stores the density output
        self.output_density['x_density'] = x.tolist()
        self.output_density['y_density'] = y_density
    
    def computeLogDensity(self, num_points, bandwidth):
        ## Transforms the input data into a matrix
        log_data = map(floats_tools.log10, self.data_np)
        density_log_data = [[x] for x in log_data]
        ## Computes the x axis
        log_min = np.amin(log_data)
        log_max = np.amax(log_data)
        log_delta = log_max - log_min
        log_density_delta = 1.1 * log_delta
        x = np.arange(
            log_min - 0.05*log_delta,
            log_max + 0.05*log_delta,
            log_density_delta / num_points
            )
        x_density = [[y] for y in x]
        ## Computes the density
        kde = KernelDensity(kernel = 'gaussian', bandwidth = bandwidth)
        kde.fit(density_log_data)
        ## kde.score_samples returns the 'log' of the density
        y_log_density = kde.score_samples(x_density).tolist()
        y_density = map(math.exp, y_log_density)
        ## Stores the density output
        self.output_log_density['x_log_density'] = x.tolist()
        self.output_log_density['y_log_density'] = y_density

    def computeOutput(self, num_points, bandwidth):
        self.output_stats = {}
        self.output_density = {}
        self.output_log_density = {}
        self.data_np = np.asarray(self.data)
        self.computeStats()
        if self.output_stats['var'] is not None and self.output_stats['var'] != 0:
            self.computeDensity(num_points, bandwidth)
            self.computeLogDensity(num_points, bandwidth)
        else:
            raise NoDensity()

    def toJSON(self, json_output_file):
        ## Linear density
        self.output = self.output_stats.copy() 
        self.output.update(self.output_density)
        with open(json_output_file + '_lin.json', 'w') as f:
            json.dump(self.output, f,
                    indent = 2, sort_keys = True)
        ## Log density
        self.output = self.output_stats.copy() 
        self.output.update(self.output_log_density)
        with open(json_output_file + '_log.json', 'w') as f:
            json.dump(self.output, f,
                    indent = 2, sort_keys = True)
   
    def plot(self, plot_output_file):
        ## Linear density
        x = self.output_density['x_density'] 
        y = self.output_density['y_density'] 
        plt.clf()
        plt.plot(x, y, 'o')
        plt.savefig(plot_output_file + '_lin.png')
        ## Log density
        x_log = self.output_log_density['x_log_density'] 
        y_log = self.output_log_density['y_log_density'] 
        plt.clf()
        plt.plot(x_log, y_log)
        plt.savefig(plot_output_file + '_log.png')

    def display(self, num_points, bandwidth, web_dataviz_dir, 
            plot_dir, output_file):
        output_file += '_n' + str(num_points) + '_b' + str(bandwidth)
        try:
            self.computeOutput(num_points, bandwidth)
            self.plot(plot_dir + output_file)
        except NoDensity:
            pass
        except ValueError:
            pass
        self.toJSON(web_dataviz_dir + output_file)

    def displayDensity(self, num_points, bandwidth, f):
        try:
            self.computeOutput(num_points, bandwidth)
        except NoDensity:
            pass
            print >>sys.stderr, 'WARNING: cannot compute a density'
        except ValueError:
            pass
            print >>sys.stderr, 'WARNING: cannot compute a density'
            print >>sys.stderr, \
                    'Exception raised by plt.plot when the y values are too small'
        ## Linear density
        self.output = self.output_stats.copy() 
        self.output.update(self.output_density)
        json.dump(self.output, f, indent = 2, sort_keys = True)
