function updatePredictionsDisplay(conf, train_test, sup_exp, fold_id) {
    if (!conf.classification_conf.probabilist_model) {
        return;
    }
    var experiment_id = conf.experiment_id;
    if (sup_exp) {
      experiment_id = sup_exp;
    }
    // Histogram
    displayPredictionsBarplot(train_test + '_predictions', conf, train_test,
                              experiment_id, fold_id,
                              displayPredictionsAnalysis(experiment_id,
                                                         train_test,
                                                         fold_id));
}
