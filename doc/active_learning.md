# Collecting an Annotated Dataset with a Reduced Workload thanks to Active Learning

SecuML allows to acquire an annotated dataset to learn a supervised detection model with a low human effort.
It is an iterative process initialized with some labelled instances. Then, at each iteration the user is asked to annotate a few
instances to improve the current detection model.

    ./SecuML_activeLearning <project> <dataset> <strategy> --init-labels-file <labels_file>

## Active Learning Strategies Available
* Ilab [1]
* Aladin [2]
* Gornitz [3]
* CesaBianchi [4]
* UncertaintySampling [5]
* RandomSampling


## Help

For more information about the available options for a given active learning strategy:

    ./SecuML_activeLearning <project> <dataset> <strategy> -h

## References
* [1] Beaugnon, Anaël, Pierre Chifflier, and Francis Bach. ["ILAB: An Interactive Labelling Strategy for Intrusion Detection."](https://www.ssi.gouv.fr/en/publication/ilab-an-interractive-labelling-strategy-for-intrusion-detection/) International Symposium on Research in Attacks, Intrusions, and Defenses. Springer, Cham, 2017.
* [2] Stokes, Jack W., et al. "Aladin: Active learning of anomalies to detect intrusions." Technique Report. Microsoft Network Security Redmond, WA 98052 (2008).
* [3] Görnitz, Nico, et al. "Active learning for network intrusion detection." Proceedings of the 2nd ACM workshop on Security and artificial intelligence. ACM, 2009.
* [4] Cesa-Bianchi, Nicolo, Claudio Gentile, and Luca Zaniboni. "Worst-case analysis of selective sampling for linear classification." Journal of Machine Learning Research 7.Jul (2006): 1205-1230.
* [5] Lewis, David D., and William A. Gale. "A sequential algorithm for training text classifiers." Proceedings of the 17th annual international ACM SIGIR conference on Research and development in information retrieval. Springer-Verlag New York, Inc., 1994.

## Graphical User Interface

### Monitoring Interface
![Active Learning Monitoring](/doc/images/AL_monitoring_1.png)

### Annotation Interface
![Active Learning Annotations](/doc/images/AL_annotations.png)

### Family Editor
![Family Editor](/doc/images/family_editor.png)

### Annotated Instances
![Annotated Instances](/doc/images/annotated_instances.png)
