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

from SecuML.Data import labels_tools

class NoAnnotationBudget(Exception):
    def __str__(self):
        return 'The annotation budget has run out'

class CheckPredictedLabels(object):

    def __init__(self, iteration):
        self.iteration = iteration
    
    ## In interactive mode, when the user annotate instances, the annotations
    ## are stored into the database.
    ## This function allows to update datasets with the new annotations,
    ## or the label modifications.
    def checkPredictedLabelsDB(self):
        self.iteration.experiment.db.commit()
        ## Updated annotations (from the confusion matrix for instance)
        self.iteration.datasets.checkLabelsWithDB(
                self.iteration.experiment.cursor,
                self.iteration.experiment.experiment_label_id)
        ## Newly labeled instances (annotated at the last iteration)
        new_labeled_instances = labels_tools.getLabeledIds(
                self.iteration.experiment.cursor,
                self.iteration.experiment.experiment_label_id,
                iteration = self.iteration.iteration_number)
        for instance_id in new_labeled_instances:
            label, sublabel, method, annotation = labels_tools.getLabelDetails(
                    self.iteration.experiment.cursor,
                    instance_id,
                    self.iteration.experiment.experiment_label_id)
            self.addLabel(instance_id, label, sublabel, method, annotation, 
                    add_db = False)

    ## If the instance is in PredictedLabels (for the given experiment)
    ## then PredictedLabels.final_label is set to "label"
    ## Then, the new label is added to Label
    ## If there is already a label for "instance_id" in "experiment"
    ## nothing is done.
    ##
    ## If the new label comes from an annotation
    ## the the budget is decremented.
    ##
    ## The datasets (labeled and unlabeled) are updated
    ## if a new label is actually added
    def addLabel(self, instance_id, label, sublabel, method, annotation, 
            add_db = True):
        if annotation:
            if self.iteration.budget <= 0:
                raise NoAnnotationBudget()
            self.iteration.budget -= 1
        if add_db:
            labels_tools.addLabel(self.iteration.experiment.cursor,
                    self.iteration.experiment.experiment_label_id,
                    instance_id, label, sublabel,
                    self.iteration.iteration_number, method, annotation)
        self.iteration.datasets.update(instance_id, label, sublabel,
                annotation)
        self.iteration.experiment.db.commit()
    
    def getTrueLabels(self, instance_ids):
        true_labels = ['malicious' if self.iteration.datasets.instances.getLabel(i, true_labels = True) else 'benign' \
                for i in instance_ids]
        return true_labels
    
    def getTrueSublabels(self, instance_ids):
        true_labels = [self.iteration.datasets.instances.getSublabel(i, true_labels = True) \
                for i in instance_ids]
        return true_labels
