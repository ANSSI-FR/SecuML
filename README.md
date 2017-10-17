# SecuML
SecuML is a Python tool that aims to foster the use of Machine Learning in Computer Security. It is distributed under the GPL2+ license.
It allows security experts to train models easily and comes up with a web user interface to visualize the results and interact with the models.
SecuML can be applied to any detection problem. It requires as input numerical features representing each instance.
It supports binary labels (malicious vs. benign) and categorical labels which represent families of malicious or benign behaviours.

#### Features
* [Training and analysing a detection model before deployment](doc/classification.md)
* [Collecting a labelled dataset with a reduced workload thanks to active learning](doc/active_learning.md)
* [Exploring a dataset interactively with rare category detection](doc/rare_category_detection.md)
* [Clustering data](doc/clustering.md)
* [Projecting data](doc/projection.md)
* [Computing descriptive statistics of each feature](doc/stats.md)

See the [documentation](doc/main.md) for more detail.


## Requirements
* rabbit-mq server (>= 3.3.5) (only for active learning and rare category detection)
* Python packages :
  * celery (>= 3.1.13) (only for active learning and rare category detection)
  * flask (>= 0.10.1)
  * flask_sqlalchemy (>= 1.0)
  * metric-learn (>= 0.3.0)
  * numpy (>= 1.8.2)
  * pandas (>= 0.14.1)
  * scikit-learn (>= 0.18.1)
  * sqlalchemy (>= 1.0.12)

#### Database
SecuML requires an access to a database (MySQL or PostgreSQL)
where the user has the following permissions: SELECT, INSERT, UPDATE, DELETE.

###### MySQL database
* MySQL server (>= 5.5.49)
* Python package :
  * mysql.connector (>= 2.1.3)

###### PostgreSQL database
* PostgreSQL server (>= 9.4.13)
* Python package :
  * psycopg2 (>= 2.5.4)

#### JS and CSS libraries
The required librairies can be dowloaded with the script `download_libraries`.

## Configuration

The environment variable `̀SECUMLCONF` must be set to the path of the configuration file which must follow the following format (see `SecuML_travis_conf.yml`):

    input_data_dir: <directory containing the input datasets>
    output_data_dir: <directory where the results of the experiments are stored>
    db_uri: <URI of the database>

## Papers and Presentations
* Beaugnon, Anaël, Pierre Chifflier, and Francis Bach. ["ILAB: An Interactive Labelling Strategy for Intrusion Detection."](https://www.ssi.gouv.fr/en/publication/ilab-an-interractive-labelling-strategy-for-intrusion-detection/) International Symposium on Research in Attacks, Intrusions, and Defenses. Springer, Cham, 2017.
* Bonneton, Anaël. ["Machine Learning for Computer Security Experts using Python & scikit-learn"](http://pyparis.org/talks.html#39d62c68337f89d3c879fff02b88e23b), PyParis, 2017.
* Bonneton, Anaël, and Antoine Husson. ["Le Machine Learning confronté aux contraintes opérationnelles des systèmes de détection."](https://www.sstic.org/2017/presentation/le_machine_learning_confront_aux_contraintes_oprationnelles_des_systmes_de_dtection/), SSTIC, 2017.

## Authors
* Anaël Beaugnon (anael.beaugnon@ssi.gouv.fr)
* Pierre Collet (pierre.collet@ssi.gouv.fr)
* Antoine Husson (antoine.husson@ssi.gouv.fr)
