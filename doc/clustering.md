# Clustering Data

The instances are clustered into a number of clusters specified by the user. Then, the user interface allows to display the instances in each cluster and to annotate instances individually or whole clusters at once.

    ./SecuML_clustering <project> <dataset> <algo> --num-clusters <num_clusters>

To display the available clustering algorithms:

	./SecuML_clustering -h

For more information about the available options for a given clustering algorithm:

	./SecuML_clustering <project> <dataset> <algo> -h

Web interface to display the results:

    http://localhost:5000/SecuML/<project>/<dataset>/Clustering/menu/

## Interface
![Clustering](/doc/images/clustering.png)
