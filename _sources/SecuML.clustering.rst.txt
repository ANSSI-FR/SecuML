.. _clustering:

##########
Clustering
##########

The instances are clustered into a number of clusters specified by the user.
Then, the user interface allows to display the instances in each cluster and to
annotate them.


*****
Usage
*****

| ``SecuML_clustering <project> <dataset> <algo>``.
| For more information about the available options for a given clustering algorithm:
| ``SecuML_clustering <project> <dataset> <algo> -h``.

Algorithms Available
====================
* Kmeans (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html>`__)
* GaussiansMixture (`scikit-learn documentation <https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html>`__)

************************
Graphical User Interface
************************

.. image:: figs/screen_shots/clustering/main.png

The top panel, Clusters Statistics, can be opened to display the number of
instances in each cluster. Selecting a cluster from the list
allows to display its instances in the
:ref:`Description panel<instance-visu>` at the bottom.
