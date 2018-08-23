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
* [optional] ``--features``: the name of the csv file containing the features;
* [optional] ``--exp-name``: the name of the experiment;
* [optional] ``--secuml-conf``: the name of the experiment.

If ``--features`` is not specified, the features are read from the file ``features.csv``.

If ``--exp-name`` is not specified, a name is automatically generated from the input parameters
of the experiment.

If ``--secuml-conf`` is not specified, the path of the configuration file is read in the environment variable
``SECUMLCONF``.

.. note::

  The features files are stored in the directory ``<input_data_dir>/<project>/<dataset>/features/`` where
  input data directory ``<input_data_dir>`` is specified in the :ref:`configuration file <configuration>`.

Visualizing the Results
-----------------------
Once an experiment has been successfully completed, the following message is displayed:

.. code-block:: bash

  Experiment <experiment_id> has been successfully completed.
  See http://localhost:5000/SecuML/<experiment_id>/ to display the results.


The results can then be displayed in the :ref:`web user interface <GUI>` with the URL provided.

.. note::

  ``SecuML_server`` must be executed to launch the web server.

Types of Experiments Available
------------------------------
* :ref:`DIADEM: Training and Diagnosing Detection Model <DIADEM>`
* :ref:`ILAB: Annotating a Dataset with a Reduced Workload <ILAB>`
* :ref:`Exploring a Dataset Interactively with Rare Category Detection <RCD>`
* :ref:`Clustering <clustering>`
* :ref:`Projection <projection>`
* :ref:`Descriptive Statistics <stats>`

Removing Experiments
--------------------

To remove all the experiments carried out for a given project:

.. code-block:: bash

    SecuML_remove_project_dataset <project>

To remove all the experiments carried out for a given dataset:

.. code-block:: bash

    SecuML_remove_project_dataset <project> --dataset <dataset>
