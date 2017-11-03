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

from __future__ import division
import copy
import json
import random
import warnings

from SecuML.Classification.ClassifierDatasets import ClassifierDatasets
from SecuML.Classification.Configuration.GaussianNaiveBayesConfiguration \
        import GaussianNaiveBayesConfiguration
from SecuML.Classification.Configuration.TestConfiguration import TestConfiguration
from SecuML.Classification.Classifiers.GaussianNaiveBayes import GaussianNaiveBayes
from SecuML.Tools import floats_tools

from Category import Category

class Categories(object):

    def __init__(self, iteration, instances, assigned_categories, assignment_proba,
                 label, category_labels):
        self.iteration           = iteration
        self.instances           = instances
        self.generateCategories(assigned_categories, assignment_proba, label,
                                category_labels)

    def numCategories(self):
        return self.num_categories

    def generateCategories(self, assigned_categories, assignment_proba, label, category_labels):
        self.assigned_categories = assigned_categories
        self.num_categories      = len(set(assigned_categories))
        self.categories = [Category(label, category_labels[x]) for x in range(self.num_categories)]
        ids = self.instances.getIds()
        for i in range(len(ids)):
            instance_id = ids[i]
            annotated   = self.instances.isAnnotated(instance_id)
            c           = self.assigned_categories[i]
            probas      = None
            if assignment_proba is not None:
                probas = assignment_proba[i, :]
            self.categories[c].addInstance(instance_id, probas, annotated)
        for c in range(self.num_categories):
            self.categories[c].finalComputation()

    @staticmethod
    def fromJson(experiment):
        categories = Categories(experiment, None, [], None)
        with open(categories.output_directory + 'categories.json', 'r') as f:
            obj = json.load(f)
            categories.num_categories = len(obj)
            categories.categories = []
            for c in range(categories.num_categories):
                categories.categories.append(Category.fromJson(obj[str(c)]))
        return categories

    def toJson(self):
        obj = {}
        for c in range(self.num_categories):
            obj[str(c)] = self.categories[c].toJson()
        return obj

    def exportAnnotationQueries(self, filename):
        obj = {}
        for c in range(self.num_categories):
            obj[self.categories[c].family] = self.categories[c].exportAnnotationQueries()
        with open(filename, 'w') as f:
            json.dump(obj, f, indent = 2)

    def annotateAuto(self, iteration):
        for c, category in enumerate(self.categories):
            category.annotateAuto(iteration)

    def getManualAnnotations(self, iteration):
        for c, category in enumerate(self.categories):
            category.getManualAnnotations(iteration)

    def checkAnnotationQueriesAnswered(self, iteration):
        for c, category in enumerate(self.categories):
            answered = category.checkAnnotationQueriesAnswered(iteration)
            if not answered:
                return False
        return True

    def generateAnnotationQueries(self, conf):
        self.setCategoryNumAnnotations(conf)
        for c, category in enumerate(self.categories):
            category.generateAnnotationQueries(conf.cluster_strategy)

    ###############
    ### Weights ###
    ###############

    def setCategoryWeights(self, category_weights):
        if category_weights == 'uniform':
            weights = self.computeCategoryUniformWeights()
        elif category_weights == 'distortion':
            weights = self.computeCategoryDistortionWeights()
        elif category_weights == 'stability':
            weights = self.computeCategoryStabilityWeights()
        elif category_weights == 'homogeneity':
            weights = self.computeCategoryHomogeneityWeights()
        else:
            raise ValueError('Invalid value for category_weights: %s.' % category_weights)
        weights = [max(w, 0.05) for w in weights]
        # The weights are normalized to sum to 1.
        if floats_tools.floatEquality(sum(weights), 0):
            weights = [1 / self.num_categories]  * self.num_categories
        else:
            weights = [w / sum(weights) for w in weights]
        for i, w in enumerate(weights):
            self.categories[i].setWeight(w)
        return weights

    def computeCategoryUniformWeights(self):
        weights = [1 / self.num_categories] * self.num_categories
        return weights

    def computeCategoryDistortionWeights(self):
        weights = [0] * self.num_categories
        for c, category in enumerate(self.num_categories):
            num = category.numInstances()
            if num > 0:
                weights[c] = 1 - sum(category[c].proba) / num
        return weights

    def computeCategoryStabilityWeights(self):
        weights = [1] * self.num_categories
        current_categories  = self.categories
        previous_categories = getattr(self.iteration.previous_iteration.annotations, self.label).categories
        if previous_categories is not None:
            current_categories_labels = [current_categories.getClusterLabel(c) for c in range(current_categories.num_categories)]
            previous_categories_labels  = [previous_categories.getClusterLabel(c) for c in range(previous_categories.num_categories)]
            for c, category_label in enumerate(current_categories_labels):
                try:
                    previous_category_id = previous_categories_labels.index(category_label)
                except:
                    continue
                previous_instances = set(previous_categories.getClusterInstances(previous_category_id, 'all', None))
                current_instances  = set(current_categories.getClusterInstances(c, 'all', None))
                w = 1 - len(previous_instances.intersection(current_instances)) / len(previous_instances.union(current_instances))
                weights[c] = w
        return weights

    def computeCategoryHomogeneityWeights(self):
        weights = [1] * self.num_categories
        current_categories  = self.categories
        if self.iteration.previous_iteration is not None:
            previous_categories = getattr(self.iteration.previous_iteration.annotations, self.label).categories
            previous_annotation_queries = getattr(self.iteration.previous_iteration.annotations, self.label).annotation_queries
            if previous_categories is not None:
                current_categories_labels = [current_categories.getClusterLabel(c) for c in range(current_categories.num_categories)]
                previous_categories_labels  = [previous_categories.getClusterLabel(c) for c in range(previous_categories.num_categories)]
                for c, category_label in enumerate(current_categories_labels):
                    try:
                        previous_category_id = previous_categories_labels.index(category_label)
                    except:
                        continue
                    prev_annotation_queries = previous_annotation_queries['c_' + str(previous_category_id)]
                    prev_annotation_queries = prev_annotation_queries['c'] + prev_annotation_queries['e'] + prev_annotation_queries['r']
                    prev_families = [self.iteration.datasets.instances.getFamily(q) for q in prev_annotation_queries]
                    if len(prev_families) == 0:
                        continue
                    else:
                        category_label_ = category_label.split('__')[1]
                        weights[c] = sum([l != category_label_ for l in prev_families]) / len(prev_families)
        return weights

    def setCategoryNumAnnotations(self, conf):
        weights = self.setCategoryWeights(conf.cluster_weights)
        num_annotations = conf.num_annotations
        annotations = [None for c in range(self.num_categories)]
        card = [self.categories[c].numInstances() - self.categories[c].num_annotated_instances \
                for c in range(self.num_categories)]
        if num_annotations > sum(card):
            num_annotations = sum(card)
            warnings.warn('The number of instances is smaller than the requested number of annotation queries. '
                          'The number of annotation queries is set to %d.' % (sum(card)))
        num_remaining_annotations = num_annotations
        no_starve_cluster = False
        while not no_starve_cluster:
            no_starve_cluster = True
            weights = [w / sum(weights) for w in weights]
            for c in range(self.num_categories):
                if annotations[c] is not None:
                    continue
                num = int(weights[c] * num_remaining_annotations)
                if card[c] <= num:
                    annotations[c]        = card[c]
                    weights[c]            = 0
                    no_starve_cluster     = False
            num_remaining_annotations = num_annotations - sum([x for x in annotations if x is not None])
            if num_remaining_annotations == 0:
                break
        for c in range(self.num_categories):
            if annotations[c] is not None:
                continue
            num              = int(weights[c] * num_remaining_annotations)
            annotations[c]   = num
        num_remaining_annotations = num_annotations - sum(annotations)
        while num_remaining_annotations > 0:
            shuffled_clusters = range(self.num_categories)
            random.shuffle(shuffled_clusters)
            for c in shuffled_clusters:
                if num_remaining_annotations == 0:
                    break
                if card[c] > annotations[c]:
                    annotations[c] += 1
                    num_remaining_annotations -= 1
        for c, num in enumerate(annotations):
            self.categories[c].setNumAnnotations(num)
        return annotations


    ##################
    ### Likelihood ###
    ##################

    def setLikelihood(self):
        naive_bayes = self.trainNaiveBayes()
        features = self.instances.getFeatures()
        for c in range(self.num_categories):
            indexes = [i for i, x in enumerate(self.assigned_categories) if x == c]
            c_features = features[indexes, :]
            c_likelihood = naive_bayes.logLikelihood(c_features, c)
            self.categories[c].setLikelihood(c_likelihood)

    def trainNaiveBayes(self):
        naive_bayes_conf = self.getNaiveBayesConf()
        datasets = ClassifierDatasets(naive_bayes_conf)
        current_families = copy.deepcopy(self.instances.families)
        # families are altered
        self.instances.families = self.assigned_categories
        datasets.train_instances = self.instances
        datasets.test_instances  = None
        datasets.setSampleWeights()
        naive_bayes = GaussianNaiveBayes(naive_bayes_conf, datasets)
        naive_bayes.training()
        # families are restored
        self.instances.families = current_families
        return naive_bayes

    def getNaiveBayesConf(self):
        test_conf = TestConfiguration()
        test_conf.setUnlabeled(labels_annotations = 'annotations')
        naive_bayes_conf = GaussianNaiveBayesConfiguration(4, False, True, test_conf)
        return naive_bayes_conf
