Use Case: Spam Detection
========================

We provide a dataset intended for spam detection for quick testing.
See `lingspam <https://github.com/ANSSI-FR/SecuML/tree/master/input_data/SpamHam/lingspam>`_ for more information.

* ``SecuML_server`` must be executed to launch the web server. ``http://localhost:5000/SecuML/`` gives access to SecuML menu.

* In the :ref:`configuration file <configuration>`, ``input_data_dir`` must be set to `input_data <https://github.com/ANSSI-FR/SecuML/tree/master/input_data/>`_ to test SecuML with the `lingspam <https://github.com/ANSSI-FR/SecuML/tree/master/input_data/SpamHam/lingspam>`_ dataset we provide.


Training and Diagnosing a Detection Model
-----------------------------------------

.. code-block:: bash

    SecuML_DIADEM SpamHam lingspam LogisticRegression --secuml-conf <path_to_your_config_file>

.. figure:: figs/screen_shots/DIADEM/performance.png

   DIADEM Monitoring Interface

See :ref:`DIADEM <DIADEM>` for more detail.

Annotating a Dataset with a Reduced Workload
--------------------------------------------

.. code-block:: bash

    SecuML_ILAB SpamHam lingspam Ilab --auto --budget 500 --secuml-conf <path_to_your_config_file>

.. figure:: figs/screen_shots/ILAB/monitoring.png

    ILAB Monitoring Interface

See :ref:`ILAB <ILAB>` for more detail.
