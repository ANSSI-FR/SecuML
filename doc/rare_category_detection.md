# Exploring a Dataset Interactively with Rare Category Detection

SecuML allows to explore a dataset interactively with rare category detection. It is an iterative process, where the user is asked to annotate some instances at each iteration.

    ./SecuML_rareCategoryDetection <project> <dataset> -f <features_files> --init-labels-file <labels_file>

For more information about the available options:

    ./SecuML_rareCategoryDetection -h

Web interface to display the results:

    http://localhost:5000/SecuML/<project>/<dataset>/ActiveLearning/menu/

## Monitoring Interface
![Rare Category Detection Monitoring](/doc/images/rare_category_detection_monitoring.png)

## Annotation Interface
![Rare Category Detection Annotations](/doc/images/rare_category_detection_annotations.png)
