Use Case: Spam Detection
========================

We provide a dataset intended for spam detection for quick testing.
See `lingspam </input_data/SpamHam/lingspam/README.md>`_ for more information.

``SecuML_server`` must be executed to launch the web server.
``http://localhost:5000/SecuML/`` gives access to SecuML menu.

Training and Diagnosing a Detection Model
-----------------------------------------

.. code-block:: bash

    SECUMLCONF=<path_to_your_config_file> SecuML_DIADEM SpamHam lingspam LogisticRegression

.. figure:: figs/screen_shots/DIADEM/performance.png

   DIADEM Monitoring Interface

See :ref:`DIADEM <DIADEM>` for more detail.

Annotating a Dataset with a Reduced Workload
--------------------------------------------

.. code-block:: bash

    SECUMLCONF=<path_to_your_config_file> SecuML_ILAB SpamHam lingspam Ilab --auto --budget 500

.. figure:: figs/screen_shots/ILAB/monitoring.png

    ILAB Monitoring Interface

See :ref:`ILAB <ILAB>` for more detail.
