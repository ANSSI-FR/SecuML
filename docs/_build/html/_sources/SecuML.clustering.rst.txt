Clustering
===========

The instances are clustered into a number of clusters specified by the user. Then, the user interface allows to display the instances in each cluster and to annotate instances individually or whole clusters at once.

.. code-block:: bash

    SecuML_clustering <project> <dataset> <algo> --num-clusters <num_clusters>

*Help*

For more information about the available options for a given clustering algorithm:

.. code-block:: bash

	SecuML_clustering <project> <dataset> <algo> -h


Algorithms Available
--------------------
* Kmeans
* GaussiansMixture

Graphical User Interface
------------------------

.. figure:: screen_shots/clustering/main.png

    Clustering Interface
