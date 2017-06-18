# Collecting a Labelled Dataset with a Reduced Workload thanks to Active Learning


SecuML allows to acquire a labelled dataset to learn a supervised detection model with a low human effort.
It is an iterative process initialized with some labelled instances. Then, at each iteration the user is asked to annotate a few
instances to improve the current detection model.

    ./SecuML_activeLearning <strategy> <project> <dataset> -f <features_files> --init-labels-file <labels_file>

To display the available labelling strategies:

    ./SecuML_activeLearning -h

For more information about the available options for a given labelling strategy:

    ./SecuML_activeLearning <strategy> -h

Web interface to display the results:

    http://localhost:5000/SecuML/<project>/<dataset>/ActiveLearning/menu/

## Monitoring Interface
![Active Learning Monitoring](/doc/images/AL_monitoring.png)

## Annotation Interface
![Active Learning Annotations](/doc/images/AL_annotations.png)
