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
* [optional] ``--exp-name``: the name of the experiment.

If ``--features`` is not specified, the features are read from the file ``features.csv``.

If ``--exp-name`` is not specified, a name is automatically generated from the input parameters
of the experiment.

.. note::

  The features files are stored in the directory ``<input_data_dir>/<project>/<dataset>/features/`` where
  input data directory ``<input_data_dir>`` is specified in the :ref:`configuration file <configuration>`.

Visualizing the Results
-----------------------
Once an experiment has been computed, its results can be displayed in the web user interface.

``http://localhost:5000/SecuML/`` gives access to SecuML menu.
It displays the list of projects and datasets available.
Besides, for each dataset, it displays the list of experiments gathered by type.

``http://localhost:5000/SecuML/<experiment_id>/`` displays directly
the results of an experiment identified by ``experiment_id``.

.. note::

  ``SecuML_server`` must be executed to launch the web server.

Types of Experiments Available
------------------------------
* :ref:`DIADEM: Training and Diagnosing Detection Model <DIADEM>`
* :ref:`ILAB: Annotating a Dataset with a Workload <ILAB>`
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
