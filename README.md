# SecuML
SecuML is a Python tool that aims to foster the use of Machine Learning in Computer Security. It is distributed under the GPL2+ license.

It allows security experts to train detection models easily and comes with a web user interface to visualize the results and interact with the models.
SecuML can be applied to any detection problem. It requires as input numerical features representing each instance.
It supports binary labels (malicious vs. benign) and categorical labels which represent families of malicious or benign behaviours.

#### Benefits of SecuML
SecuML relies on [scikit-learn](https://www.scikit-learn.org/stable/index.html) to train the Machine Learning models
and offers the additionnal features:
* **_Web user interface_**   
  diagnosis and interaction with Machine Learning models (active learning, rare category detection)
* **_Hide some of the Machine Learning machinery_**   
  automation of data loading, feature standardization, and search of the best hyperparameters

#### What you can do with SecuML
* Training and diagnosing a detection model before deployment with DIADEM
* Annotating a dataset with a reduced workload with ILAB
* Exploring a dataset interactively with rare category detection
* Clustering
* Projection
* Computing descriptive statistics of each feature

See the [sphinx documentation](https://anssi-fr.github.io/SecuML/) for more detail.

#### Papers
* Beaugnon, Anaël, Pierre Chifflier, and Francis Bach. ["End-to-End Active Learning for Computer Security Experts."](https://www.ssi.gouv.fr/uploads/2018/02/end-to-end-active-learning-for-computer-security-experts_abeaugnon_pchifflier_fbach_anssi_inria.pdf)   
AAAI Workshop on Artificial Intelligence for Computer Security (AICS 2018).
* Beaugnon, Anaël, Pierre Chifflier, and Francis Bach. ["ILAB: An Interactive Labelling Strategy for Intrusion Detection."](https://www.ssi.gouv.fr/uploads/2017/09/ilab_beaugnonchifflierbach_raid2017.pdf)   
International Symposium on Research in Attacks, Intrusions and Defenses (RAID 2017).
* [FRENCH] Bonneton, Anaël, and Antoine Husson. ["Le Machine Learning confronté aux contraintes opérationnelles des systèmes de détection."](https://www.sstic.org/media/SSTIC2017/SSTIC-actes/le_machine_learning_confront_aux_contraintes_oprat/SSTIC2017-Article-le_machine_learning_confront_aux_contraintes_oprationnelles_des_systmes_de_dtection-bonneton_husson.pdf)   
Symposium sur la sécurité des technologies de l'information et des communications (SSTIC 2017).

#### PhD Dissertation
* Beaugnon, Anaël. ["Expert-in-the-Loop Supervised Learning for Computer Security Detection Systems."](https://www.ssi.gouv.fr/uploads/2018/06/beaugnon-a_these_manuscrit.pdf)   
Ph.D. thesis, École Normale Superieure (2018)

#### Presentations
* [FRENCH] Beaugnon, Anaël. ["Appliquer le Machine Learning de manière pertinente à la détection d’intrusion."](https://www.cert-ist.com/pub/files/Forum2017-03-Anael_Beaugnon-Machine-Learning.pdf)   
Forum annuel du CERT-IST (CERT-IST 2017).
* Bonneton, Anaël. ["Machine Learning for Computer Security Experts using Python & scikit-learn."](http://pyparis.org/talks.html#39d62c68337f89d3c879fff02b88e23b)   
PyParis 2017.

#### Authors
* Anaël Beaugnon (anael.beaugnon@ssi.gouv.fr)
* Pierre Collet (pierre.collet@ssi.gouv.fr)
* Antoine Husson (antoine.husson@ssi.gouv.fr)
