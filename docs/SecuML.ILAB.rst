.. _ILAB:

ILAB: Interactive LABeling
==========================

Collecting an Annotated Dataset with a Reduced Workload thanks to Active Learning

ILAB allows to acquire an annotated dataset to learn a supervised detection model with a low human effort.
It is an iterative process initialized with some annotated instances. Then, at each iteration the user is asked to annotate a few
instances to improve the current detection model.

.. code-block:: bash

    SecuML_ILAB <project> <dataset> <strategy>

*Help*

For more information about the available options for a given active learning strategy:

.. code-block:: bash

    SecuML_ILAB <project> <dataset> <strategy> -h


Strategies Available
--------------------
* Ilab [1,2]
* Aladin [3]
* Gornitz [4]
* CesaBianchi [5]
* UncertaintySampling [6]
* RandomSampling


*References*

* [1] Beaugnon et al., `"End-to-End Active Learning for Computer Security Experts" <https://www.ssi.gouv.fr/uploads/2018/02/end-to-end-active-learning-for-computer-security-experts_abeaugnon_pchifflier_fbach_anssi_inria.pdf>`_, AICS 2018.
* [2] Beaugnon et al., `"ILAB: An Interactive Labelling Strategy for Intrusion Detection" <https://www.ssi.gouv.fr/uploads/2017/09/ilab_beaugnonchifflierbach_raid2017.pdf>`_, RAID 2017.
* [3] Stokes et al., Aladin: "Active learning of anomalies to detect intrusions", technical report 2008.
* [4] Görnitz et al, "Active learning for network intrusion detection", AISEC 2009.
* [5] Cesa-Bianchi et al., "Worst-case analysis of selective sampling for linear classification", JMLR 2006.
* [6] Lewis et al., "A sequential algorithm for training text classifiers", 1994.

Graphical User Interface
------------------------

.. figure:: screen_shots/ILAB/monitoring.png

    Monitoring Interface

.. figure:: screen_shots/ILAB/annotations.png

    Annotation Interface

.. figure:: screen_shots/ILAB/family_editor.png

    Family Editor

.. figure:: screen_shots/ILAB/annotated_instances.png

    Annotated Instances
