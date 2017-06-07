# SecuML
SecuML is a Python tool that aims to foster the use of Machine Learning in Computer Security. It is distributed under the GPL2+ license.
It allows security experts to train models easily and
comes up with a web user interface to visualize the results and interact with the models.
SecuML can be applied to any detection problem. It requires as input numerical features representing each instance.
It supports binary labels (malicious vs. benign) and categorical labels which represent families of malicious or benign behaviours.

#### Features
* [Training and analysing a detection model before deployment](doc/classification.md)
* [Collecting a labelled dataset with a reduced workload thanks to active learning](doc/active_learning.md)
* [Exploring a dataset interactively with rare category detection](doc/rare_category_detection.md)
* [Clustering data](doc/clustering.md)
* [Projecting data](doc/projection.md)
* [Computing descriptive statistics of each feature](doc/stats.md)


## Requirements and Configurations

#### Requirements
* rabbit-mq server (>= 3.3.5) (only for active learning and rare category detection)
* MySQL server (>= 5.5.49)
* Python packages:
  * celery (>= 3.1.13) (only for active learning, and rare category detection)
  * flask (>= 0.10.1)
  * metric-learn (>= 0.3.0)
  * mysql.connector (>=2.1.3)
  * numpy (>= 1.8.2)
  * pandas (>= 0.14.1)
  * scikit-learn (>= 0.18.1)

#### Initial Configurations

##### MySQL
MySQL must be configured with a `my.cnf` file with the following format:

	[client]
	host=<host>
	user=<user>
	password=<password>

The MySQL user must have the following permissions: SELECT, INSERT, UPDATE, DELETE, CREATE and DROP.

##### JS and CSS libraries
The required librairies can be dowloaded with the script `download_libraries`.

## Datasets
SecuML considers projects which correspond to different detection problems (PDF files , PE, Android applications or Spam for instance).
For a given project, several datasets can be used.
The directory `SecuML/input_data/<project>/<dataset>/` must contain the following informations about a given dataset:

* `idents.csv`: A csv file containing the identifiers of the instances (header: `instance_id, ident`).
* a `features` directory: It contains csv files with the features of the instances (header: `instance_id, names of the features`).
* a `labels` directory: It contains csv files with the labels associated to the instances (header: `instance_id,label`, or `instance_id,label,family`, and the end of line character must be LF).
Labels are either `malicious` or `benign`.  Families regroup similar malicious or benign instances.
If the ground truth labels are known, they must be stored in the file `true_labels.csv`.

See `SecuML/input_data/SpamHam/lingspam/` for an example of dataset ([Lingspam Dataset](input_data/SpamHam/lingspam/README.md)).

## Experiments

To display the results of the experiments in the web user interface the server must be launched

    ./SecuML_server

To remove all the experiments carried out for a given project

    ./SecuML_remove_project_dataset <project>

To remove all the experiments carried out for a given dataset

    ./SecuML_remove_project_dataset <project> --dataset <dataset>
