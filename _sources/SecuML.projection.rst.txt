.. _projection:

##########
Projection
##########

The data are projected into a lower-dimensional space for visualization. The user interface allows to display the instances in a plane defined by two components.
The instances are not displayed individually but with an hexagonal binning (color from green to black according to the number of instances in the bin).
The color of the dot in the middle of each bin (from yellow to red) corresponds to the proportion of known malicious instances in the bin.


*****
Usage
*****

| ``SecuML_projection <project> <dataset> <algo>``.
| For more information about the available options for a given projection algorithm:
| ``SecuML_projection <project> <dataset> <algo> -h``.

Algorithms Available
====================

Unsupervised Algorithms
-----------------------
* Pca (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`__)

Semi-supervised Algorithms
--------------------------
* Rca (`metric-learn documentation <https://metric-learn.github.io/metric-learn/metric_learn.rca.html>`__)
* Lda (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html>`__)
* Lmnn (`metric-learn documentation <https://metric-learn.github.io/metric-learn/metric_learn.lmnn.html>`__)
* Nca (`metric-learn documentation <https://metric-learn.github.io/metric-learn/metric_learn.nca.html>`__)
* Itml (`metric-learn documentation <https://metric-learn.github.io/metric-learn/metric_learn.itml.html>`__)


************************
Graphical User Interface
************************

.. image:: figs/screen_shots/projection/main.png
