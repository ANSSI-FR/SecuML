# Getting Started

We provide a dataset intended for spam detection for quick testing.
See [lingspam](/input_data/SpamHam/lingspam/README.md) for more information.

## Seeting up SecuML
First, you need to install the requirements and set the configuration file.
See [Requirements and Configuration](/doc/requirements_configuration.md) for the instructions.

`input_data_dir` must be set to [`input_data`](/input_data) in the configuration file to test SecuML with the dataset we provide.

## Web User Interface
SecuML comes up with a web user interface to display the results of the analysis and interact with the Machine Learning models.
The analyses must be run from the command line. Once they are computed, the results can be displayed in the web user interface.

To launch the web server :

    ./SecuML_server

To display the results in a web browser :

    http://localhost:5000/SecuML/

## Training and Analysing a Detection Model before Deployment

#### Command line to launch the experiment

    SECUMLCONF=<path_to_your_config_file> ./SecuML_classification SpamHam lingspam LogisticRegression

#### Screen shot of the monitoring interface

![Classification](/doc/images/classification.png)

See [Classification](/doc/classification.md) for more detail.

## Collecting an Annotated Dataset with a Reduced Workload thanks to Active Learning

#### Command line to launch the experiment

    SECUMLCONF=<path_to_your_config_file> ./SecuML_activeLearning SpamHam lingspam Ilab --auto --budget 500

#### Screen shot of the monitoring interface
![Active Learning Monitoring](/doc/images/AL_monitoring_1.png)

See [Active Learning](/doc/active_learning.md) for more detail.
