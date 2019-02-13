function updatePredictionsDisplay(train_test, child_exp_id) {
    if (!classifier_conf.probabilist) {
        return;
    }
    displayPredictionsBarplot(train_test + '_predictions',
                              child_exp_id,
                              displayPredictionsAnalysis(child_exp_id));
}
