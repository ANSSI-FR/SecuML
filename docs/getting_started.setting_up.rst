Setting up SecuML
=================


SecuML comes with a web user interface to display the results of the analysis
and interact with the Machine Learning models.
The analyses must be run from the command line.
Once they are computed, the results can be displayed in the web user interface.


Database
--------
SecuML requires an access to a database. MySQL and PostgreSQL are supported.
The user must have the following permissions:
``SELECT``, ``INSERT``, ``UPDATE``, ``DELETE``, ``CREATE TEMPORARY TABLES``.
The URI of the database must be specified in SecuML
:ref:`configuration file <configuration>`.

*MySQL database*

* MySQL server
* Python package

    + mysql.connector

*PostgreSQL database*

* PostgreSQL server
* Python package

    + psycopg2-binary


Installation
------------

Requirements
""""""""""""

+ rabbitmq-server
+ Python packages

    * celery
    * flask
    * flask_sqlalchemy
    * matplotlib
    * metric-learn
    * numpy
    * pandas
    * scikit-learn (== 0.21.2)
    * seaborn
    * sqlalchemy
    * yaml

Automatic Installation
"""""""""""""""""""""""

.. code-block:: bash

    virtualenv venv_SecuML --no-site-packages --python python3
    source venv_SecuML/bin/activate
    pip install <path_to_SecuML_project>

.. note::

    SecuML works with python 3.5, 3.6 and 3.7.


.. _configuration:

Configuration
-------------

SecuML requires a configuration file that follows the following format:

.. code-block:: yaml

    input_data_dir: <directory containing the input datasets>
    output_data_dir: <directory where the results of the experiments are stored>
    db_uri: <URI of the database>
    logger_level: <[optional] DEBUG,INFO,WARNING,ERROR or CRITICAL - default INFO>
    logger_output: <[optional] name of the logging output file - default sys.stderr>
    host: <[optional] host of the web server - default localhost>
    port: <[optional] port number of the web server - default 8080>

See `SecuML_conf_template.yml <https://github.com/ANSSI-FR/SecuML/blob/master/conf/SecuML_conf_template.yml>`_.

Input and Output Directories
""""""""""""""""""""""""""""
.. warning::

    `input_data_dir` and `output_data_dir` must contain **absolute paths**.


* The input directory contains the datasets that will be analyzed by SecuML. See :ref:`Data <Data>` for more information.

* The output directory contains all the results of the SecuML experiments. Users should not read the results from this directory directly, but rather from the :ref:`web user interface <GUI>`.

.. note::

    ``input_data_dir`` must be set to
    `input_data <https://github.com/ANSSI-FR/SecuML/tree/master/input_data/>`_
    in the configuration file to test SecuML with the dataset we provide.


Database URI
""""""""""""

The format of the database URI depends on its type:

* MySQL database

  .. code-block:: bash

      mysql+mysqlconnector://<user>:<password>@<host>/<db_name>


* PostgreSQL database

  .. code-block:: bash

      postgresql://<user>:<password>@<host>/<db_name>

Logging Parameters
"""""""""""""""""""

Logging parameters (``logger_level`` and ``logger_output``) are optional.
By default, logging is displayed in the standard error with ``INFO`` level.

Web Server Parameters
"""""""""""""""""""""

The web server parameters (``host`` and ``port``) are optional.
By default, the web serveur binds to ``localhost`` on port ``8080``.


.. _GUI:

Web User Interface
------------------

SecuML comes with a web user interface to display the results of the
experiments, and to interact with machine learning models
(see :ref:`ILAB <ILAB>` and :ref:`Rare Category Detection <RCD>`).

You can launch the web server with the following command line.

.. code-block:: bash

    SecuML_server --secuml-conf <path_to_conf_file>

``http://<host>:<port>/SecuML/`` gives access to SecuML menu.
It displays the list of projects and datasets available.
Besides, for each dataset, it displays the list of experiments gathered by
type.

``http://<host>:<port>/SecuML/<experiment_id>/`` displays directly
the results of an experiment identified by ``experiment_id``.

.. note::

  The configuration file is required to run SecuML executables
  (e.g. ``SecuML_server``, ``SecuML_DIADEM``, ``SecuML_ILAB``).
  It can be specified either with the parameter ``--secuml-conf`` for each
  execution, or globally with the environment variable ``SECUMLCONF``.
