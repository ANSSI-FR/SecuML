## Installation

First, you need to install the requirements and set the configuration file.
See [Requirements and Configuration](/doc/requirements_configuration.md) for the instructions.

`input_data_dir` must be set to [`input_data`](/input_data) in the configuration file to test SecuML with the dataset we provide.

## Datasets
SecuML considers projects which correspond to different detection problems (PDF files , PE, Android applications or Spam for instance).
For a given project, several datasets can be used.
The directory `<input_data_dir>/<project>/<dataset>/` must contain the following items:

* `idents.csv`: A csv file containing the identifiers of the instances (header: `instance_id, ident`).
* a `features` directory: It contains csv files with the features of the instances (header: `instance_id, names of the features`).
* a `labels` directory: It contains csv files with the labels associated to the instances (header: `instance_id,label`, or `instance_id,label,family`, and the end of line character must be LF).
Labels are either `malicious` or `benign`.  Families regroup similar malicious or benign instances.
If the ground truth labels are known, they must be stored in the file `true_labels.csv`.

See [`input_data/SpamHam/lingspam/`](/input_data/SpamHam/lingspam/) for an example of dataset.


## Web User Interface
SecuML comes up with a web user interface to display the results of the analysis and interact with the Machine Learning models.
The analyses must be run from the command line. Once they are computed, the results can be displayed in the web user interface.

To launch the web server :

    ./SecuML_server

To display the results in a web browser :

    http://localhost:5000/SecuML/


## Experiments

To remove all the experiments carried out for a given project:

    ./SecuML_remove_project_dataset <project>

To remove all the experiments carried out for a given dataset:

    ./SecuML_remove_project_dataset <project> --dataset <dataset>


## What you can do with SecuML:
* [Training and analysing a detection model before deployment](/doc/classification.md)
* [Collecting a labelled dataset with a reduced workload thanks to active learning](/doc/active_learning.md)
* [Exploring a dataset interactively with rare category detection](/doc/rare_category_detection.md)
* [Clustering](/doc/clustering.md)
* [Projection](/doc/projection.md)
* [Computing descriptive statistics of each feature](/doc/stats.md)
