#!/bin/bash

set -e

function experiments {
    SecuML_features_analysis Gaussians test
    SecuML_projection Gaussians test -a GROUND_TRUTH Lda
    SecuML_clustering Gaussians test Kmeans
    SecuML_DIADEM Gaussians test LogisticRegression
    SecuML_DIADEM Gaussians test LogisticRegression --multiclass
    SecuML_DIADEM Gaussians test GradientBoosting --alerts-classif GaussianNaiveBayes
    SecuML_DIADEM Gaussians test GradientBoosting --alerts-clustering Kmeans --num-alerts-clusters 3
    SecuML_DIADEM Gaussians test LogisticRegression --validation-mode ValidationDatasets --validation-datasets test --streaming
    SecuML_ILAB Gaussians test -a init_annotations.csv Random --auto
    SecuML_rm_project_exp --exp-id 1
    SecuML_rm_project_exp --project Gaussians
}

SECUMLCONF=conf/travis_psql.yml experiments
SECUMLCONF=conf/travis_mysql.yml experiments
