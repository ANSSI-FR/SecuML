function updatePredictionsDisplay(train_test, child_exp_id, with_links) {
    displayPredictionsBarplot(train_test + '_pred', child_exp_id,
                              displayPredictionsAnalysis, with_links);
}
