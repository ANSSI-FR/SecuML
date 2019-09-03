.. _experiments:

Experiments
===========

.. _exp-params:

Running Experiments
-------------------
The experiments must be run from the command line.
Each type of experiment has its own executable
(e.g. ``SecuML_DIADEM``, ``SecuML_ILAB``).

All the experiments share the following arguments:

* ``project``: the name of the project;
* ``dataset``: the name of the dataset belonging to ``project``;
* [optional] ``--features``: csv file or directory containing the features;
* [optional] ``--filter-in``: csv file containing the features to use;
* [optional] ``--filter-out``: csv file containing the features to filter out;
* [optional] ``--exp-name``: the name of the experiment;
* [optional] ``--secuml-conf``: the path of the configuration file.

If ``--features`` is not specified, the features are read from the file
``features.csv``.
If a directory is provided, then all the files of the directory are
concatenated to build the input features.

The parameters ``--filter-in`` and ``--filter-out`` are mutually exclusive.
File format: one feature id per line.

If ``--exp-name`` is not specified, a name is automatically generated from the
input parameters of the experiment.

If ``--secuml-conf`` is not specified, the path of the configuration file is
read in the environment variable ``SECUMLCONF``.

.. note::

  The features files are stored in the directory
  ``<input_data_dir>/<project>/<dataset>/features/`` where
  input data directory ``<input_data_dir>`` is specified in the
  :ref:`configuration file <configuration>`.

Visualizing the Results
-----------------------
Once an experiment has been successfully completed, the following message is
displayed:

.. code-block:: bash

  Experiment <experiment_id> has been successfully completed.
  See http://<host>:<port>/SecuML/<experiment_id>/ to display the results.


The results can then be displayed in the :ref:`web user interface <GUI>` with
the URL provided.

.. note::

  ``SecuML_server`` must be executed to launch the web server.

Types of Experiments Available
------------------------------
* :ref:`DIADEM: Training and Diagnosing Detection Model <DIADEM>`
* :ref:`ILAB: Annotating a Dataset with a Reduced Workload <ILAB>`
* :ref:`Exploring a Dataset Interactively with Rare Category Detection <RCD>`
* :ref:`Clustering <clustering>`
* :ref:`Projection <projection>`
* :ref:`Features Analysis <stats>`

Removing Experiments
--------------------

To remove all the experiments carried out for a given project:

.. code-block:: bash

    SecuML_rm_project_exp --project <project>

To remove a given experiment:

.. code-block:: bash

    SecuML_rm_project_exp --exp-id <exp_id>
