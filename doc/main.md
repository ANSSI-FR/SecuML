## Datasets
SecuML considers projects which correspond to different detection problems (PDF files , PE, Android applications or Spam for instance).
For a given project, several datasets can be used.
The directory `<input_data_dir>/<project>/<dataset>/` must contain the following informations about a given dataset:

* `idents.csv`: A csv file containing the identifiers of the instances (header: `instance_id, ident`).
* a `features` directory: It contains csv files with the features of the instances (header: `instance_id, names of the features`).
* a `labels` directory: It contains csv files with the labels associated to the instances (header: `instance_id,label`, or `instance_id,label,family`, and the end of line character must be LF).
Labels are either `malicious` or `benign`.  Families regroup similar malicious or benign instances.
If the ground truth labels are known, they must be stored in the file `true_labels.csv`.

See `SecuML/input_data/SpamHam/lingspam/` for an example of dataset ([Lingspam Dataset](input_data/SpamHam/lingspam/README.md)).

## Experiments

The server must be launched to display the results of the experiments in the web user interface:

    ./SecuML_server

To remove all the experiments carried out for a given project:

    ./SecuML_remove_project_dataset <project>

To remove all the experiments carried out for a given dataset:

    ./SecuML_remove_project_dataset <project> --dataset <dataset>

## Types of Experiments
* [Training and analysing a detection model before deployment](doc/classification.md)
* [Collecting a labelled dataset with a reduced workload thanks to active learning](doc/active_learning.md)
* [Exploring a dataset interactively with rare category detection](doc/rare_category_detection.md)
* [Clustering data](doc/clustering.md)
* [Projecting data](doc/projection.md)
* [Computing descriptive statistics of each feature](doc/stats.md)
