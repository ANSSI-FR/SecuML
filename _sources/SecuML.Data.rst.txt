.. _Data:

Data
====

SecuML considers projects which correspond to different detection problems
on different data types
(PDF files , PE, Android applications or Spam for instance).
For a given project, several datasets can be used.
The directory ``<input_data_dir>/<project>/<dataset>/`` must contain the
following items a file ``idents.csv``, a ``features`` and an ``annotations``
directories.
See `input_data/SpamHam/lingspam/ <https://github.com/ANSSI-FR/SecuML/tree/master/input_data/SpamHam/lingspam>`_
for an example of input dataset.

.. note::

  The input data directory ``<input_data_dir>`` is specified in the
  :ref:`configuration file <configuration>`.

``idents.csv``
^^^^^^^^^^^^^^
A csv file containing the identifiers of the instances.
It has the following columns:

* **instance_id**: integer ;
* **ident**: string describing the instance ;
* **[optional] timestamp**: date (``YYYY-MM-DD HH:MM:SS`` format) of the instance.

The timestamps are required for
:ref:`DIADEM's temporal validation modes <diadem-validation-modes>`.

``features`` directory
^^^^^^^^^^^^^^^^^^^^^^
It contains csv files with the features of the instances.
It has the following columns:

* **instance_id**: integer ;
* **a column for each feature**: numeric (float or integer).

.. warning::

  The instances in the features files must be stored in the same order as in
  ``idents.csv``.

The header of a features csv file ``<filename>.csv`` may be human-readable
names or integer ids.
Names and more detailed descriptions can be associated to
each feature in a file called ``<filename>_description.csv``.
This description file is optional.

Some features files can be stored in a folder to run experiments
on several files. In this case, the features of the different
files are concatenated to build a dataset.
See :ref:`exp-params` for more information.

.. note::

  SecuML supports only boolean and numerical features.
  Categorical features are not supported yet.

``annotations`` directory
^^^^^^^^^^^^^^^^^^^^^^^^^
It contains csv files with the annotations associated to the instances.
It has the following columns:

* **instance_id**: integer ;
* **label**: binary label, ``malicious`` or ``benign`` ;
* **[optional] family**: string.

**Families**

Families detail the binary label.
Instances sharing the same family behave similarly.
For example, malicious instances belonging to the same family may exploit the
same vulnerability, they may be polymorphic variants of the same malware, or
they may be email messages coming from the same spam campaign.

:ref:`ILAB <ILAB>` and :ref:`rare category detection <RCD>` require that the
families are specified.
Besides, the families can be leveraged by :ref:`DIADEM <DIADEM>` to cluster
alerts according to user-defined malicious families.

**Ground Truth and Partial Annotations**

If the ground truth is known, it must be stored in the file
``annotations/ground_truth.csv``.

.. warning::

  The instances in ``annotations/ground_truth.csv`` must be stored in the same
  order as in ``idents.csv``.

If only some instances are annotated, their annotations can be stored, in any
order, in an annotation file ``annotations/<filename>.csv``.

Partial annotations are required for
:ref:`DIADEM <diadem>`, :ref:`ILAB <ILAB>` and
:ref:`rare category detection <RCD>`.
:ref:`Clustering <clustering>`, :ref:`projection <projection>`, and
:ref:`features analysis <stats>` do not require annotations,
but they can be leveraged to ease analyses.
