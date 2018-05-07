# ILAB: Interactive LABeling  
#### Collecting an Annotated Dataset with a Reduced Workload thanks to Active Learning

ILAB allows to acquire an annotated dataset to learn a supervised detection model with a low human effort.
It is an iterative process initialized with some annotated instances. Then, at each iteration the user is asked to annotate a few
instances to improve the current detection model.

    ./SecuML_ILAB <project> <dataset> <strategy> --init-labels-file <labels_file>

## Active Learning Strategies Available
* Ilab [1,2]
* Aladin [3]
* Gornitz [4]
* CesaBianchi [5]
* UncertaintySampling [6]
* RandomSampling


## Help

For more information about the available options for a given active learning strategy:

    ./SecuML_ILAB <project> <dataset> <strategy> -h

## References
* [1] Beaugnon, Anaël, Pierre Chifflier, and Francis Bach. ["End-to-End Active Learning for Computer Security Experts."](https://www.ssi.gouv.fr/uploads/2018/02/end-to-end-active-learning-for-computer-security-experts_abeaugnon_pchifflier_fbach_anssi_inria.pdf)  
AAAI Workshop on Artificial Intelligence for Computer Security (AICS 2018).
* [2] Beaugnon, Anaël, Pierre Chifflier, and Francis Bach. ["ILAB: An Interactive Labelling Strategy for Intrusion Detection."](https://www.ssi.gouv.fr/uploads/2017/09/ilab_beaugnonchifflierbach_raid2017.pdf)  
International Symposium on Research in Attacks, Intrusions and Defenses (RAID 2017).
* [3] Stokes, Jack W., et al. "Aladin: Active learning of anomalies to detect intrusions."  
Technique Report. Microsoft Network Security Redmond, WA 98052 (2008).
* [4] Görnitz, Nico, et al. "Active learning for network intrusion detection."  
Workshop on Security and Artificial Intelligence, 2009.
* [5] Cesa-Bianchi, Nicolo, Claudio Gentile, and Luca Zaniboni. "Worst-case analysis of selective sampling for linear classification."  
Journal of Machine Learning Research (JMLR 2006).
* [6] Lewis, David D., and William A. Gale. "A sequential algorithm for training text classifiers."  
Annual international conference on Research and development in information retrieval, 1994.

## Graphical User Interface

### Monitoring Interface
![Active Learning Monitoring](/doc/images/AL_monitoring_1.png)

### Annotation Interface
![Active Learning Annotations](/doc/images/AL_annotations.png)

### Family Editor
![Family Editor](/doc/images/family_editor.png)

### Annotated Instances
![Annotated Instances](/doc/images/annotated_instances.png)
