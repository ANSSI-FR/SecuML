.. _DIADEM:

#####################################
DIADEM: DIAgnosis of DEtection Models
#####################################

**Training and Analysing a Detection Model before Deployment.**

DIADEM trains and evaluates detection models
(:ref:`supervised<DIADEM_supervised>`,
:ref:`semi-supervised<DIADEM_semisupervised>` and
:ref:`unsupervised<DIADEM_unsupervised>`).
It hides some of the machine learning machinery
(feature standardization,
:ref:`setting of the hyperparameters<DIADEM_hyperparameters>`)
to let security experts focus mainly on detection.
Besides, it comes with a :ref:`graphical user interface <diadem-gui>` to
evaluate and diagnose detection models.

.. rubric:: References

* Beaugnon, Anaël, and Pierre Chifflier. `"Machine Learning for Computer Security Detection Systems: Practical Feedback and Solutions" <https://www.ssi.gouv.fr/uploads/2018/11/machine-learning-for-computer-security-abeaugnon-pchifflier-anssi-.pdf>`_, C&ESAR 2018.
* Beaugnon, Anaël. `"Expert-in-the-Loop Supervised Learning for Computer Security Detection Systems." <https://www.ssi.gouv.fr/uploads/2018/06/beaugnon-a_these_manuscrit.pdf>`_, Ph.D. thesis, École Normale Superieure (2018).
* [FRENCH] Bonneton, Anaël, and Antoine Husson, `"Le Machine Learning confronté aux contraintes opérationnelles des systèmes de détection" <https://www.sstic.org/media/SSTIC2017/SSTIC-actes/le_machine_learning_confront_aux_contraintes_oprat/SSTIC2017-Article-le_machine_learning_confront_aux_contraintes_oprationnelles_des_systmes_de_dtection-bonneton_husson.pdf>`_, SSTIC 2017.

*****
Usage
*****

| **Semi-supervised and supervised model classes:**
| ``SecuML_DIADEM <project> <dataset> <model_class> -a <annotations_file>``.

| **Unsupervised model classes:**
| ``SecuML_DIADEM <project> <dataset> <model_class>``.

.. note::

    These arguments are enough to launch DIADEM on a given dataset.
    The parameters presented below are completely optional.

The following sections present the :ref:`model classes available
<DIADEM_model_classes>`, and some **optional parameters** for
:ref:`setting the hyperparameters<DIADEM_hyperparameters>`
and :ref:`selecting a specific validation mode<DIADEM-validation-modes>`.
If these parameters are not provided,
DIADEM uses default values for the hyperparameters, and splits the input
dataset into a training (90%) and a validation dataset (10%).


.. _DIADEM_model_classes:

Model Classes
=============

.. _DIADEM_supervised:

Supervised Model Classes
------------------------
* LogisticRegression (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html>`__)
* Svc (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html>`__)
* GaussianNaiveBayes (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html>`__)
* DecisionTree (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier>`__)
* RandomForest (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html>`__)
* GradientBoosting (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html>`__)

.. _DIADEM_unsupervised:

Unsupervised Model Classes
--------------------------
* Lof (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html>`__)
* IsolationForest (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html>`__)
* OneClassSvm (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html>`__)
* EllipticEnvelope (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.covariance.EllipticEnvelope.html>`__)

.. _DIADEM_semisupervised:

Semi-supervised Model Classes
-----------------------------
* LabelPropagation (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.semi_supervised.LabelPropagation.html>`__)
* Sssvdd (new implementation)


| For more information about the available options for a given model class:
| ``SecuML_DIADEM <project> <dataset> <model_class> -h``.


.. _DIADEM_hyperparameters:

Hyperparameters
===============
Some model classes have *hyperparameters*, i.e. parameters that must be set
before the training phase. These parameters are not fit automatically
by the training algorithm.

For example, logistic regression has two hyperparameters: the regularization
strength, ``--regularization``, and the penalty norm, ``--penalty``.
The number of trees, ``--n-estimators``, is one hyperparameter of random
forests among many others.

Hyperparameters Values
----------------------
To list the hyperparameters of a given detection model see the
*Hyperparameters* group of the help message displayed by
``SecuML_DIADEM <project> <dataset> <model_class> -h``.
For each hyperparameter, the help message displays its name and its default
value.

Semi-supervised and unsupervised model classes accept only a single value
for each hyperparameter. On the contrary, supervised model classes
accept a list of values for each hyperparameter, and the best combination
of hyperparameters is selected automatically with a grid-search.

Automatic Selection
-------------------
In the case of supervised model classes, DIADEM selects the best combination
of hyperparameters automatically. It considers all the combinations
of hyperparameters values in a *grid search* to find the best one.
First, DIADEM evaluates the performance (through :ref:`cross-validation <cv>`)
of the detection model trained with each combination, then it selects the one
that results in the best-performing detection model.

DIADEM allows to parametrize the grid search:

* [optional] ``--num-folds``: number of folds built in the cross-validation (default: 4);
* [optional] ``--n-jobs``:  number of CPU cores used when parallelizing the cross-validation, -1 means using all cores (default: -1);
* [optional] ``--objective-func``: the performance indicator (``Ndcg``, ``RocAuc``, ``Accuracy``, or ``DrAtFdr``) to optimize during the grid-search (default: ``RocAuc``). ;
* [optional] ``--far``: the false alarm rate (far) to consider if ``--objective-func`` is set to ``DrAtFdr``.

These options are listed in the *Hyperparameters Optimization* group of the help
message displayed by
``SecuML_DIADEM <project> <dataset> <supervised_model_class> -h``.


.. _DIADEM-validation-modes:

Validation Modes
================
DIADEM offers several validation modes, i.e. ways to build the training and the
validation datasets.
Temporal validation modes (:ref:`temporal-split`, :ref:`cutoff-time`,
:ref:`temporal-cv`, and :ref:`sliding-window`) should be preferred when
the instances are timestamped since they better reflect real-world conditions.
These validation modes ensure that no instance from the future is used when the
detection model is trained:
the training instances predate the validation instances.

.. _random-split:

Random Split
------------
``--test-mode RandomSplit --test-size <prop>``

``<prop>`` instances of ``<dataset>`` are selected uniformly for the validation
dataset. The remaining instances constitute the training dataset.

.. _temporal-split:

Temporal Split
--------------
``--test-mode TemporalSplit --test-size <prop>``

The ``<prop>`` most recent instances of ``<dataset>`` are selected for the
validation dataset. The remaining instances constitute the training dataset.

.. _cutoff-time:

Cutoff Time
-----------
``--test-mode CutoffTime --cutoff-time <cutoff_time>``

The instances of ``<dataset>`` with a timestamp before ``<cutoff_time>``
constitutes the training dataset, and the instances after constitute the
validation dataset.
``<cutoff_time>`` must be formatted as follows:
``YYYY-MM-DD HH:MM:SS``.

.. _cv:

Cross Validation
----------------

``--test-mode Cv --validation-folds <num_folds>``

The dataset ``<dataset>`` is divided uniformly into ``<num_folds>`` buckets.
Each bucket has approximately the same number
of instances and the same proportion of benign/malicious instances as the whole
dataset.
The detection model is trained ``<num_folds>`` times: each time, one bucket is
the validation dataset and the other buckets form the training dataset.

*Example with* :math:`\text{num_folds} = 4`:

.. image::  figs/validation_diagrams/cv.svg
   :width: 90%
   :align: center

.. _temporal-cv:

Temporal Cross Validation
-------------------------
``--test-mode TemporalCv --validation-folds <num_folds>``

The dataset ``<dataset>`` is divided into ``<num_folds> + 1`` buckets.
Each bucket :math:`b_{i \in [0,~\text{num_folds}]}` contains instances
occurring between :math:`t_i^{max} = T^{min} + i \cdot \Delta`
and :math:`t_i^{max} = T^{min} + (i+1) \cdot \Delta`
where

* :math:`T^{min}` and :math:`T^{max}` correspond to the timestamps of the oldest and latest instances ;

* :math:`\Delta = \frac{T^{max} - T^{min}}{\text{num_folds} + 1}`.

For each fold :math:`f\in[0,\text{num_folds}-1]`, the buckets from :math:`b_0`
to :math:`b_f` constitute the training dataset, and the remaining buckets form
the validation dataset.

*Example with* :math:`\text{num_folds} = 4`:

.. image::  figs/validation_diagrams/temporal_cv.svg
   :width: 90%
   :align: center

.. _sliding-window:

Sliding Window
--------------

``--test-mode SlidingWindow --buckets <n> --train-buckets <n_train> --test-buckets <n_test>``

The dataset ``<dataset>`` is divided into ``<n>`` buckets
just as in the case of :ref:`temporal-cv`.
Each bucket :math:`b_{i \in [0,~n-1]}` contains instances
occurring between :math:`t_i^{max} = T^{min} + i \cdot \Delta`
and :math:`t_i^{max} = T^{min} + (i+1) \cdot \Delta`
where

* :math:`T^{min}` and :math:`T^{max}` correspond to the timestamps of the oldest and latest instances ;

* :math:`\Delta = \frac{T^{max} - T^{min}}{n}`.

For each fold :math:`f\in[0,n-(n_{train}+n_{test})+1]`,
the buckets from :math:`b_{f}`
to :math:`b_{f+n_{train}}` constitute
the training dataset, and the buckets from :math:`b_{f+n_{train}}`
to :math:`b_{f+n_{train}+n_{test}}`
form the validation dataset.

*Example with* :math:`n = 5`, :math:`n_{train} = 2` and :math:`n_{test} = 1`.

.. image::  figs/validation_diagrams/sliding_window.svg
   :width: 90%
   :align: center

.. _validation-dataset:

Validation Dataset
------------------

``--test-mode ValidationDataset --validation-dataset <validation_dataset>``

The whole dataset ``<dataset>`` constitutes the training data, and
``<validation_dataset>`` constitutes the validation data.


Applying a Previous Detection Model
===================================

DIADEM can apply a previously trained detection model with the following
command line:

.. code-block:: bash

    SecuML_DIADEM <project> <dataset> AlreadyTrained --model-exp-id <exp_id> \
        --test-mode ValidationDataset --validation-dataset <validation_dataset>

In this case, there are two restrictions:

* ``--model-exp-id`` must correspond to a
  :ref:`DIADEM <DIADEM>` or an :ref:`ILAB <ILAB>` experiment ;
* ``ValidationDataset`` is the only validation mode available.


.. _diadem-gui:

************************
Graphical User Interface
************************

Model Performance and Predictions
=================================
DIADEM displays the performance evaluation and the predictions of the detection
model both on the training and validation datasets.
The predictions analysis is always available,
while the performance evaluation can be computed only when the data are
annotated.

**Performance.**
The *Performance* tab displays the detection and the false alarm rates
for a given detection threshold.
The value of the detection threshold can be modified through a slider
to see the impact on the detection and false alarm rates.
The confusion matrix and the ROC curve are also displayed.
See :ref:`misc_detection_perf_metrics` for more information.

.. _performance-tab:

.. figure:: figs/screen_shots/DIADEM/performance.png
  :align: center

  Performance Tab

**Predictions.**
The *Predictions* tab displays the histograms of the predicted probabilities of
maliciousness.
When annotations are available, the instances are grouped by label.

.. _predictions-tab:

.. figure:: figs/screen_shots/DIADEM/histograms.png
  :align: center

  Predictions Tab

Model Behavior
==============
DIADEM displays information about the global behavior of detection models.
This visualization allows to grasp how detection models make decisions
and to diagnose potential training biases.

It is currently implemented for linear (see :ref:`linear-model-coeff`)
and tree-based (see :ref:`tree-model-importance`) models.
DIADEM does not yet support model-agnostic interpretation methods.

These graphic depictions allow a focus on the most influential features
of the detection model.
Clicking on a given feature gives access to its descriptive statistics on the
training data (see :ref:`Features Analysis <stats>`).
These statistics allow to understand why a feature has a significant impact on
decision-making, and may point out biases in the training dataset.

.. _linear-model-coeff:

.. figure:: figs/screen_shots/DIADEM/logistic_regression_coefficients.png
  :width: 49%
  :align: center

  Features Coefficients of a Linear Model

.. _tree-model-importance:

.. figure:: figs/screen_shots/DIADEM/random_forest_importance.png
  :width: 49%
  :align: center

  Features Importance of a Tree-based Model


Individual Predictions
======================
DIADEM diagnosis interface also allows to examine individual predictions.
For example, the false positives and negatives can be reviewed
by clicking on the confusion matrix displayed by the :ref:`performance-tab`.

Besides, the :ref:`predictions-tab` allows to analyze the instances
whose predicted probability is within a given range.
For instance, the instances close to the decision boundary
(probability of maliciousness close to 50%) can be reviewed
to understand why the detection model is undecided.
Moreover, the instances that have been misclassified with a high level of
confidence can be inspected to point out potential annotation errors, or help
finding new discriminating features.

**Description Panel**

DIADEM displays each instance in a :ref:`Description panel<instance-visu>`.
By default, all the values of the features of the instance are displayed.
Other visualizations specific to the detection problem may be more relevant to
analyze individual predictions. In order to address this need, SecuML enables
users to plug :ref:`problem-specific visualizations <problem-specific-visu>`.

If an interpretable model has been trained, DIADEM also displays
the features that have the most impact on the prediction
(see :ref:`important-features` ).
This visualization is easier to interpret than the previous one
since the features are sorted according to their impact in the decision-making
process.

.. _important-features:

.. figure:: figs/screen_shots/DIADEM/feature_weights.png
  :width: 80%
  :align: center

  Most Important Features
