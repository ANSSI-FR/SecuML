.. _DIADEM:

DIADEM: DIAgnosis of DEtection Models
=====================================

Training and Analysing a Detection Model before Deployment

A supervised detection model is learned from an annotated dataset, and applied to a validation dataset (annotated or not).
The GUI displays performance indicators (detection rate, false alarm rate, f-score, ROC, AUC, confusion matrix, ...)
of the detection model on the training dataset and on the validation dataset (if ground-truth labels are available).
The false positives and negatives can be displayed from the confusion matrix.
The GUI also allows to analyze the alerts raised on the validation dataset
(the top N alerts, randomly selected alerts, or a clustering of the alerts).

.. code-block:: bash

    SecuML_DIADEM <project> <dataset> <model_class>

*Help*

For more information about the available options for a given model class:

.. code-block:: bash

	SecuML_DIADEM <project> <dataset> <model_class> -h


Model Classes Available
-----------------------
* LogisticRegression
* Svc
* GaussianNaiveBayes
* DecisionTree
* RandomForest
* GradientBoosting

*References*

* [FRENCH] Bonneton, Anaël, and Antoine Husson, `"Le Machine Learning confronté aux contraintes opérationnelles des systèmes de détection", <https://www.sstic.org/media/SSTIC2017/SSTIC-actes/le_machine_learning_confront_aux_contraintes_oprat/SSTIC2017-Article-le_machine_learning_confront_aux_contraintes_oprationnelles_des_systmes_de_dtection-bonneton_husson.pdf>`_, SSTIC 2017.

Graphical User Interface
------------------------

.. figure:: screen_shots/DIADEM/main.png

    DIADEM Monitoring Interface
