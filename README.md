# SecuML
SecuML is a Python tool that aims to foster the use of Machine Learning in Computer Security. It is distributed under the GPL2+ license.
It allows security experts to train models easily and comes up with a web user interface to visualize the results and interact with the models.
SecuML can be applied to any detection problem. It requires as input numerical features representing each instance.
It supports binary labels (malicious vs. benign) and categorical labels which represent families of malicious or benign behaviours.

#### What you can do with SecuML:
* [Training and analysing a detection model before deployment](/doc/classification.md)
* [Collecting a labelled dataset with a reduced workload thanks to active learning](/doc/active_learning.md)
* [Exploring a dataset interactively with rare category detection](/doc/rare_category_detection.md)
* [Clustering](/doc/clustering.md)
* [Projection](/doc/projection.md)
* [Computing descriptive statistics of each feature](/doc/stats.md)

See the [documentation](/doc/main.md) for more detail.

#### Getting Started
We provide a dataset intended for spam detection for quick testing.
See [Getting Started](/doc/getting_started.md) for the instructions.

#### Papers and Presentations
* Beaugnon, Anaël, Pierre Chifflier, and Francis Bach. ["ILAB: An Interactive Labelling Strategy for Intrusion Detection."](https://www.ssi.gouv.fr/en/publication/ilab-an-interractive-labelling-strategy-for-intrusion-detection/) International Symposium on Research in Attacks, Intrusions, and Defenses. Springer, Cham, 2017.
* Bonneton, Anaël. ["Machine Learning for Computer Security Experts using Python & scikit-learn"](http://pyparis.org/talks.html#39d62c68337f89d3c879fff02b88e23b), PyParis, 2017.
* Bonneton, Anaël, and Antoine Husson. ["Le Machine Learning confronté aux contraintes opérationnelles des systèmes de détection."](https://www.sstic.org/2017/presentation/le_machine_learning_confront_aux_contraintes_oprationnelles_des_systmes_de_dtection/), SSTIC, 2017.

#### Authors
* Anaël Beaugnon (anael.beaugnon@ssi.gouv.fr)
* Pierre Collet (pierre.collet@ssi.gouv.fr)
* Antoine Husson (antoine.husson@ssi.gouv.fr)
