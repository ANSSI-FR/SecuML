# Requirements and Configuration

## Requirements
* rabbit-mq server (>= 3.3.5) (only for active learning and rare category detection)
* Python packages :
  * celery (>= 3.1.13) (only for active learning and rare category detection)
  * flask (>= 0.10.1)
  * flask_sqlalchemy (>= 1.0)
  * metric-learn (>= 0.3.0)
  * numpy (== 1.12.1)
  * pandas (== 0.19.2)
  * scikit-learn (== 0.18.1)
  * sqlalchemy (>= 1.0.12)
  * yaml (>= 3.11)

#### Automatic installation

    python setup.py install

#### Database
SecuML requires an access to a database (MySQL or PostgreSQL)
where the user has the following permissions: SELECT, INSERT, UPDATE, DELETE, CREATE TEMPORARY TABLES.

###### MySQL database
* MySQL server (>= 5.5.49)
* Python package :
  * mysql.connector (>= 2.1.3)

###### PostgreSQL database
* PostgreSQL server (>= 9.4.13)
* Python package :
  * psycopg2 (>= 2.5.4)

#### Web User Interface
The required JS and CSS librairies can be dowloaded with the script [`download_libraries`](/download_libraries).

## Configuration

The environment variable `̀SECUMLCONF` must be set to the path of the configuration file which must follow the following format
(see [`SecuML_travis_conf.yml`](/SecuML_travis_conf.yml)):

    input_data_dir: <directory containing the input datasets>
    output_data_dir: <directory where the results of the experiments are stored>
    db_uri: <URI of the database>

`input_data_dir` must be set to [`input_data`](\input_data) in the configuration file to test SecuML with the dataset we provide.
