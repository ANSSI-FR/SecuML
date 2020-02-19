.. _Data:

Data
====

SecuML considers projects which correspond to different detection problems
on different data types
(PDF files , PE, Android applications or Spam for instance).
For a given project, several datasets can be used.
The directory ``<input_data_dir>/<project>/<dataset>/`` must contain the
following items: a file ``idents.csv``, a ``features`` and an ``annotations``
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
* **[optional] timestamp**: date (``YYYY-MM-DD HH:MM:SS`` format) of the instance ;
* **[optional] label**: boolean, ground truth label (0 for ``benign`` and 1 for ``malicious``) ;
* **[optional] family**: string, ground truth family.

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

The features can also be stored in a sparse format.
CSC, CSR and LIL
`scipy sparse formats <https://scikit-learn.org/stable/developers/performance.html>`_
are supported.
In this case, a description file (see below) must be provided
to describe the features.

.. _features_description_file:

Optional features description file: ``<features_filename>_description.csv``
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
The header of a features csv file ``<features_filename>.csv`` may be
human-readable names or integer ids.
Names and more detailed descriptions can be associated to
each feature in a file called ``<features_filename>_description.csv``.
This description file is optional and it has the following columns:

* **id**: feature id (the sames as in ``<features_filename>.csv``) ;
* **name**: string describing the feature ;
* **[optional] description**: longer string describing the feature ;
* **[optional] type**: type of the feature (``numeric`` or ``binary``).

SecuML supports only boolean and numerical features.
Categorical features are not supported yet.

.. note::

   If you provide the features' types in a description file,
   SecuML will load the dataset more quickly
   since it does not need to infer them.


Folder of features files
""""""""""""""""""""""""
Some features files can be stored in a folder to run experiments
on several files. In this case, the features of the different
files are concatenated to build a dataset.
See :ref:`exp-params` for more information.


``annotations`` directory
^^^^^^^^^^^^^^^^^^^^^^^^^
The ground truth labels and families are stored in the ``idents.csv``
file.
If only some instances are annotated, their annotations can be stored
in a CSV annotation file ``annotations/<filename>.csv`` with the following
columns:

* **instance_id**: integer ;
* **label**: boolean, 0 for ``benign`` and 1 for ``malicious``;
* **[optional] family**: string.

Partial annotations are required for
:ref:`DIADEM <diadem>`, :ref:`ILAB <ILAB>` and
:ref:`rare category detection <RCD>`.
:ref:`Clustering <clustering>`, :ref:`projection <projection>`, and
:ref:`features analysis <stats>` do not require annotations,
but they can be leveraged to ease analyses.

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
