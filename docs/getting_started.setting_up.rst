Seeting up SecuML
=================

Installation
------------

Requirements
""""""""""""

+ rabbit-mq server (>= 3.3.5) (only for active learning and rare category detection)
+ Python packages

    * celery (>= 3.1.13) (only for :ref:`ILAB <ILAB>` and :ref:`rare category detection <RCD>`)
    * flask (>= 0.10.1)
    * flask_sqlalchemy (>= 1.0)
    * matplotlib (>= 2.1.1)
    * metric-learn (>= 0.4.0)
    * numpy (== 1.12.1)
    * pandas (== 0.19.2)
    * scikit-learn (== 0.19.0)
    * sqlalchemy (>= 1.0.12)
    * yaml (>= 3.11)

Automatic Installation
"""""""""""""""""""""""

.. code-block:: bash

    virtualenv venv_SecuML --no-site-packages --python python3
    source venv_SecuML/bin/activate
    python3 setup.py install

.. warning::

    The dependencies stored in `requirements.txt` are automatically installed by `setup.py`.
    They cannot be installed with `pip install -r requirements.txt` because the required version
    of `metric-learn` has not been released on PyPI yet.


Web User Interface
------------------

SecuML comes with a web user interface to display the results of the analysis and interact with the Machine Learning models.
The analyses must be run from the command line.
Once they are computed, the results can be displayed in the web user interface.


Database
""""""""
SecuML requires an access to a database. MySQL and PostgreSQL are supported.
The user must have the following permissions: ``SELECT``, ``INSERT``, ``UPDATE``, ``DELETE``, ``CREATE TEMPORARY TABLES``.

*MySQL database*

* MySQL server (>= 5.5.49)
* Python package

    + mysql.connector (>= 2.1.3, <= 2.1.4)

*PostgreSQL database*

+ PostgreSQL server (>= 9.4.13)
+ Python package

    + psycopg2-binary (>= 2.5.4)

JS and CSS
""""""""""

The required JS and CSS librairies can be dowloaded with the script `download_libraries </download_libraries>`_.

*The JS dependencies must be stored in* ``SecuML/web/static/lib/js``:

* bootstrap.min.js (>= 3.3.0) ;
* d3.min.js (>= 3.5.17) ;
* jquery.min.js (>= 3.1.0) ;
* Chart.min.js (>= 2.2.2).

*The CSS dependencies must be stored in* ``SecuML/web/static/lib/js``:

* bootstrap.min.css (>= 3.3.7) ;
* jquery-ui.min.css (>= 1.12.1).

.. _configuration:

Configuration
-------------

The configuration file must follow the following format (see `SecuML_travis_conf.yml </conf/SecuML_travis_conf.yml>`_):

.. code-block:: yaml

    input_data_dir: <directory containing the input datasets>
    output_data_dir: <directory where the results of the experiments are stored>
    db_uri: <URI of the database>

``input_data_dir`` must be set to `input_data <\input_data>`_ in the configuration file to test SecuML with the dataset we provide.

The environment variable ``SECUMLCONF`` must be set to the path of the configuration file.
