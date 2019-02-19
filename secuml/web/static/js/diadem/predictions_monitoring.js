function updatePredictionsDisplay(train_test, child_exp_id) {
    displayPredictionsBarplot(train_test + '_pred', child_exp_id,
                              displayPredictionsAnalysis(child_exp_id));
}
