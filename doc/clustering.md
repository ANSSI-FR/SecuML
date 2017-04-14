# Clustering Data

The instances are clustered into a number of clusters specified by the user. Then, the user interface allows to display the instances in each cluster and to annotate instances individually or whole clusters at once.

    ./SecuML_clustering <project> <dataset> -f <features_files> --clustering-algo <Kmeans/GaussianMixture> --num-clusters <num_clusters>

For more information about the available options:

	./SecuML_clustering -h

Web interface to display the results:

    http://localhost:5000/SecuML/<project>/<dataset>/Clustering/menu/

## Interface
![Clustering](/doc/images/clustering.png)
