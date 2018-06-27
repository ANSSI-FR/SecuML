Running SecuML on the lingspam dataset
======================================

We provide a dataset intended for spam detection for quick testing.
See `lingspam </input_data/SpamHam/lingspam/README.md>`_ for more information.

Training and diagnosing a detection model before deployment with DIADEM
-----------------------------------------------------------------------

.. code-block:: bash

    SECUMLCONF=<path_to_your_config_file> SecuML_DIADEM SpamHam lingspam LogisticRegression

.. figure:: screen_shots/DIADEM/main.png

   DIADEM monitoring interface.

See :ref:`DIADEM <DIADEM>` for more detail.

Annotating a dataset with a reduced workload with ILAB
-------------------------------------------------------

.. code-block:: bash

    SECUMLCONF=<path_to_your_config_file> SecuML_ILAB SpamHam lingspam Ilab --auto --budget 500

.. figure:: screen_shots/ILAB/monitoring.png

    ILAB monitoring interface

See :ref:`ILAB <ILAB>` for more detail.
