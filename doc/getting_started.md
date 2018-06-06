# Getting Started


## Seeting up SecuML

### Installation and Configuration
First, you need to install the requirements and set the configuration file.
See [Requirements and Configuration](/doc/requirements_configuration.md) for the instructions.

`input_data_dir` must be set to [`input_data`](/input_data) in the configuration file to test SecuML with the dataset we provide.

### Web User Interface
SecuML comes up with a web user interface to display the results of the analysis and interact with the Machine Learning models.
The analyses must be run from the command line. Once they are computed, the results can be displayed in the web user interface.

To launch the web server :

    SecuML_server

To display the results in a web browser :

    http://localhost:5000/SecuML/


## Running SecuML on the lingspam dataset

We provide a dataset intended for spam detection for quick testing.
See [lingspam](/input_data/SpamHam/lingspam/README.md) for more information.

### Training and diagnosing a detection model before deployment with DIADEM

##### Command line to launch the experiment

    SECUMLCONF=<path_to_your_config_file> SecuML_DIADEM SpamHam lingspam LogisticRegression

##### Screen shot of the monitoring interface

![Classification](/doc/images/DIADEM/classification.png)

See [DIADEM](/doc/DIADEM.md) for more detail.

### Annotating a dataset with a reduced workload with ILAB

#### Command line to launch the experiment

    SECUMLCONF=<path_to_your_config_file> SecuML_ILAB SpamHam lingspam Ilab --auto --budget 500

#### Screen shot of the monitoring interface
![Active Learning Monitoring](/doc/images/ILAB/AL_monitoring.png)

See [ILAB](/doc/ILAB.md) for more detail.


## Running SecuML on your own dataset

### Input datasets (features and annotation)
SecuML considers projects which correspond to different detection problems (PDF files , PE, Android applications or Spam for instance).
For a given project, several datasets can be used.
The directory `<input_data_dir>/<project>/<dataset>/` must contain the following items:

* `idents.csv`: A csv file containing the identifiers of the instances (header: `instance_id, ident`).
* a `features` directory: It contains csv files with the features of the instances (header: `instance_id, names of the features`).
* a `annotations` directory: It contains csv files with the annotations associated to the instances (header: `instance_id,label`, or `instance_id,label,family`, and the end of line character must be LF).
Labels are either `malicious` or `benign`.  Families regroup similar malicious or benign instances.
If the ground truth labels are known, they must be stored in the file `ground_truth.csv`.

See [`input_data/SpamHam/lingspam/`](/input_data/SpamHam/lingspam/) for an example of dataset.

### Problem-specific visualizations
SecuML web user interface displays individual instances (e.g. errors from the confusion matrix with DIADEM, or instances to annotate with ILAB) in a `Description` panel.
By default, the `Description` panel displays only the features of the instance.
This visualization may be hard to interpret especially when the feature space is in high dimension.

SecuML enables to plug problem-specific visualizations for each project
(the datasets belonging to the same project share the same problem-specific visualizations).
They should be easily interpretable by security experts and display the most relevant elements from a detection perspective.
They may point out to external tools or information to provide some context.
Several custom visualizations can be implemented (in different tabs) to show the instances from various angles.

##### JavaScript code
The code must be stored in `SecuML/web/static/js/InstancesInformation/<project>.js`. See [`SecuML/web/static/js/InstancesInformation/SpamHam.js`](/SecuML/web/static/js/InstancesInformation/SpamHam.js) for an example.

##### Flask code
The code must be stored in `SecuML/web/views/Projects/<project>.py`. See [`SecuML/web/views/Projects/SpamHam.py`](/SecuML/web/views/Projects/SpamHam.py) for an example.
