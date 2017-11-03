# Training and Analysing a Detection Model before Deployment

A supervised detection model is learned from an annotated dataset, and applied to a validation dataset (annotated or not).
The GUI displays performance indicators (detection rate, false alarm rate, f-score, ROC, AUC, confusion matrix, ...)
of the detection model on the training dataset and on the validation dataset (if ground truth labels are available).
The false positives and negatives can be displayed from the confusion matrix.
The GUI also allows to analyse the alerts raised on the validation dataset
(the top N alerts, randomly selected alerts, or a clustering of the alerts).

    ./SecuML_classification <project> <dataset> <model_class>
    ./SecuML_classification <project> <dataset> <model_class> --validation-dataset <validation_dataset>

## Model Classes Available
* LogisticRegression
* Svc
* GaussianNaiveBayes
* DecisionTree
* RandomForest
* GradientBoosting

## Help

For more information about the available options for a given model class:

	./SecuML_classification <project> <dataset> <model_class> -h

## Reference
* Bonneton, Anaël, and Antoine Husson. ["Le Machine Learning confronté aux contraintes opérationnelles des systèmes de détection."](https://www.sstic.org/2017/presentation/le_machine_learning_confront_aux_contraintes_oprationnelles_des_systmes_de_dtection/), SSTIC, 2017.

## Graphical User Interface
![Classification](/doc/images/classification.png)

