Data and Problem-Specific Visualizations
========================================

Data
----

SecuML considers projects which correspond to different detection problems
on different data types
(PDF files , PE, Android applications or Spam for instance).
For a given project, several datasets can be used.
The directory ``<input_data_dir>/<project>/<dataset>/`` must contain the following items
a file ``idents.csv``, a ``features`` and an ``annotations`` directories.
See `input_data/SpamHam/lingspam/ </input_data/SpamHam/lingspam/>`_ for an example of input dataset.

.. note::

  The input data directory ``<input_data_dir>`` is specified in the :ref:`configuration file <configuration>`.

``idents.csv``
^^^^^^^^^^^^^^
A csv file containing the identifiers of the instances.
It has the following columns:

* **instance_id**: integer ;
* **ident**: string describing the instance ;
* **[optional] timestamp**: date (``YYYY-MM-DD HH:MM:SS`` format) of the instance.

The timestamps are required for :ref:`DIADEM's temporal validation modes <diadem-validation-modes>`.

``features`` directory
^^^^^^^^^^^^^^^^^^^^^^
It contains csv files with the features of the instances.
It has the following columns:

* **instance_id**: integer ;
* **a column for each feature**: numeric (float or integer).

.. warning::

  The instances in the features files must be stored in the same order as in ``idents.csv``.

SecuML does not take raw data as input, but data that has already been transformed into
fixed-length vectors of features.
Currently, SecuML supports only numerical features.

``annotations`` directory
^^^^^^^^^^^^^^^^^^^^^^^^^
It contains csv files with the annotations associated to the instances.
It has the following columns:

* **instance_id**: integer ;
* **label**: binary label, ``malicious`` or ``benign`` ;
* **[optional] family**: string.

.. warning::

  The end of line character of the annotations file must be LF.

**Families**

Families detail the binary label.
Instances sharing the same family behave similarly.
For example, malicious instances belonging to the same family may exploit the same vulnerability,
they may be polymorphic variants of the same malware, or they may be email messages
coming from the same spam campaign.

:ref:`ILAB <ILAB>` and :ref:`rare category detection <RCD>` require that the families are specified.
Besides, the families can be leveraged by :ref:`DIADEM <DIADEM>` to cluster alerts according to
user defined malicious families.

**Ground Truth and Partial Annotations**

If the ground truth is known, it must be stored in the file ``annotations/ground_truth.csv``.

.. warning::

  The instances in ``annotations/ground_truth.csv`` must be stored in the same order as in ``idents.csv``.

If only some instances are annotated, their annotations can be stored, in any order,
in an annotation file ``annotations/<filename>.csv``.

The ground truth is required to train supervised detection models with :ref:`DIADEM <diadem>`.
Partial annotations are required for :ref:`ILAB <ILAB>` and :ref:`rare category detection <RCD>`.
:ref:`Clustering <clustering>`, :ref:`projection <projection>`, and :ref:`descriptive statistics <stats>`
do not require any annotation file, but annotations can be leveraged to ease analysis.

.. _problem-specific-visu:

Problem-Specific Visualizations
-------------------------------
SecuML web user interface displays individual instances (e.g. errors from the confusion matrix with DIADEM, or instances to annotate with ILAB) in a *Description* panel.
By default, the *Description* panel displays only the features of the instance.
This visualization may be hard to interpret especially when the feature space is in high dimension.

SecuML enables to plug problem-specific visualizations for each project
(the datasets belonging to the same project share the same problem-specific visualizations).
They should be easily interpretable by security experts and display the most relevant elements from a detection perspective.
They may point out to external tools or information to provide some context.
Several custom visualizations can be implemented (in different tabs) to show the instances from various angles.

Implementation
^^^^^^^^^^^^^^
.. note::

  Problem-specific visualizations are not required to use SecuML web user interface.
  However, we strongly encourage to implement convenient problem-specific visualizations,
  since they can significantly ease the analysis of individual instances.

JavaScript code
"""""""""""""""
| The code must be stored in ``SecuML/web/static/js/InstancesInformation/<project>.js``.
| See `SecuML/web/static/js/InstancesInformation/SpamHam.js </SecuML/web/static/js/InstancesInformation/SpamHam.js>`_ for an example.

Flask code
""""""""""
| The code must be stored in ``SecuML/web/views/Projects/<project>.py``.
| See `SecuML/web/views/Projects/SpamHam.py </SecuML/web/views/Projects/SpamHam.py>`_) for an example.
