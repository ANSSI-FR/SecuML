.. _lingspam-use-case:

Use Case: Spam Detection
========================
We provide a dataset intended for spam detection for quick testing.
See `lingspam <https://github.com/ANSSI-FR/SecuML/tree/master/input_data/SpamHam/lingspam>`_ for more information.

* ``SecuML_server`` must be executed to launch the :ref:`web server <GUI>`. ``http://<host>:<port>/SecuML/`` gives access to SecuML menu.

  .. code-block:: bash

    SecuML_server --secuml-conf <path_to_conf_file>


* In the :ref:`configuration file <configuration>`, ``input_data_dir`` must be set to `input_data <https://github.com/ANSSI-FR/SecuML/tree/master/input_data/>`_ to test SecuML with the `lingspam <https://github.com/ANSSI-FR/SecuML/tree/master/input_data/SpamHam/lingspam>`_ dataset we provide.

.. note::

  The configuration file is required to run SecuML executables (e.g. ``SecuML_server``, ``SecuML_DIADEM``, ``SecuML_ILAB``).
  It can be specified either with the parameter ``--secuml-conf`` for each execution, or globally
  with the environment variable ``SECUMLCONF``.


Training and Diagnosing a Detection Model
-----------------------------------------

.. code-block:: bash

    SecuML_DIADEM SpamHam lingspam --secuml-conf <conf_file> LogisticRegression

.. figure:: figs/screen_shots/DIADEM/performance.png

   DIADEM Monitoring Interface

See :ref:`DIADEM <DIADEM>` for more detail.

Annotating a Dataset with a Reduced Workload
--------------------------------------------

.. code-block:: bash

    SecuML_ILAB SpamHam lingspam --secuml-conf <conf_file> Ilab --auto --budget 500

.. figure:: figs/screen_shots/ILAB/monitoring.png

    ILAB Monitoring Interface

See :ref:`ILAB <ILAB>` for more detail.
