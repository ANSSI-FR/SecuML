# SecuML
SecuML allows to build Machine Learning models for computer security detection problems and comes with a web user interface. It is distributed under the GPL2+ license.
SecuML can be applied to any detection problem. It requires as input numerical features representing each instance. It supports binary labels (malicious vs. benign) and categorical sublabels which represent families of malicious or benign behaviours. It offers the following features:

* Learning a Supervised Detection Model and Analysing the Alerts
* Projecting Data
* Clustering Data
* Acquiring a Labeled Dataset with a Reduced Human Effort

#### Requirements
* MySQL server (>= 5.5.49)
* Python packages:
 + flask (>= 0.10.1)
 + metric-learn (>= 0.3.0)
 + mysql.connector (>=2.1.3)
 + numpy (>= 1.8.2)
 + pandas (>= 0.14.1)
 + scikit-learn (>= 0.18.1)
 
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
SecuML considers projects which correspond to different detection problems (PDF files , PE, Android applications or Spam for instance). For a given project, several datasets can be used. The directory `SecuML/input_data/<project>/<dataset>/` must contain the following informations about a given dataset:

* `idents.csv`: A csv file containing the identifiers of the instances (header: `instance_id, ident`).
* a `features` directory: It contains csv files with the features of the instances (header: `instance_id, names of the features`).
* a `labels` directory: It contains csv files with the labels associated to the instances (header: `instance_id,label`, or `instance_id,label,sublabel`, and the end of line character must be LF).
Labels are either `malicious` or `benign`.  Sublabels correspond to user defined families for a given label.
If the ground truth labels are known, they must be stored in the file `true_labels.csv`.

See `SecuML/input_data/SpamHam/lingspam/` for an example of dataset ([Lingspam Dataset] (input_data/SpamHam/lingspam/README.md)).

## Experiments

To display the results of the experiments in the web user interface the server must be lauched

    ./SecuML_server

To remove all the experiments carried out for a given project

    ./SecuML_remove_project_dataset <project>

To remove all the experiments carried out for a given dataset

    ./SecuML_remove_project_dataset <project> --dataset <dataset>

* **Learning a Supervised Detection Model and Analysing the Alerts**

A supervised detection model is learned from a labeled dataset, and applied to a validation dataset (labeled or not).  The GUI displays performance indicators (detection rate, false alarm rate, f-score, ROC, AUC, confusion matrix, ...) of the detection model on the training dataset and on the validation dataset (if ground truth labels are available). The false positives and negatives can be displayed from the confusion matrix.  The GUI also allows to analyse the alerts raised on the validation dataset (the top N alerts, randomly selected alerts, or a clustering of the alerts).

    ./SecuML_supervised_learning <project> <dataset> -f <features_files>
    ./SecuML_supervised_learning <project> <dataset> -f <features_files> --validation-dataset <validation_dataset>

For more information about the available options:

	./SecuML_supervised_learning -h

Web interface to display the results:
	
	http://localhost:5000/SecuML/<project>/<dataset>/SupervisedLearning/menu/


Screen shot of the interface for an experiment run on the lingspam dataset:
![Supervised Learning](/images/supervised_learning.png)

* **Projecting Data**

The data are projected into a lower-dimensional space for visualization. The user interface allows to display the instances in a plane defined by two components. The instances are not displayed individually but with an hexagonal binning (color from green to black according to the number of instances in the bin). The color of the dot in the middle of each bin (from yellow to red) corresponds to the proportion of known malicious instances in the bin.

    ./SecuML_projection <project> <dataset> -f <features_files> --algo <Pca/Lda/Lmnn>

For more information about the available options:

    ./SecuML_projection -h

Web interface to display the results:
	
    http://localhost:5000/SecuML/<project>/<dataset>/Projection/menu/

Screen shot of the interface for an experiment run on the lingspam dataset:
![Projection](/images/projection.png)

* **Clustering Data**
	
The instances are clustered into a number of clusters specified by the user. Then, the user interface allows to display the instances in each cluster and to annotate instances individually or whole clusters at once.
    
    ./SecuML_clustering <project> <dataset> -f <features_files> --clustering-algo <Kmeans/GaussianMixture> --num-clusters <num_clusters>

For more information about the available options:

	./SecuML_clustering -h

Web interface to display the results:

    http://localhost:5000/SecuML/<project>/<dataset>/Clustering/menu/

Screen shot of the interface for an experiment run on the lingspam dataset:
![Clustering](/images/clustering.png)

* **Acquiring a Labeled Dataset with a Reduced Human Effort**

This program allows to acquire a labeled dataset to learn a supervised detection model with a low human effort.
It is an iterative process initialized with some labeled instances. Then, at each iteration the user is asked to annotate a few
instances to improve the current detection model.

    ./SecuML_active_learning <project> <dataset> -f <features_files> --init-labels-file <labels_file>

For more information about the available options:

    ./SecuML_active_learning -h

Web interface to display the results:

    http://localhost:5000/SecuML/<project>/<dataset>/ActiveLearning/menu/

Screen shot of the interface for an experiment run on the [NSL-KDD] (http://www.unb.ca/research/iscx/dataset/iscx-NSL-KDD-dataset.html) dataset:
![Active Learning](/images/active_learning.png)
