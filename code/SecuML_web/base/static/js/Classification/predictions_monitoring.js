function updatePredictionsDisplay(conf, train_test, sup_exp) {
    if (!conf.classification_conf.probabilist_model) {
        return;
    }
    var exp = conf.experiment_id;
    if (sup_exp) {
      exp = sup_exp;
    }
    // Histogram
    var histogram = cleanDiv(train_test + '_predictions');
    displayPredictionsBarplot(histogram, conf, train_test, exp);
}

function displayPredictionsBarplot(div_obj, conf, train_test, exp) {
  if (validationWithoutTrueLabels(train_test, conf, exp_type)) {
    var get_function = 'predictions_barplot';
  } else {
    var get_function = 'predictions_barplot_labels';
  }
  var query = buildQuery('supervisedLearningMonitoring',
                         [conf.project, conf.dataset, exp, train_test, get_function]);
  callback = null;
  if (conf.exp_type == 'Classification') {
    callback = displayPredictionsAnalysis(train_test);
  }
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data);
      var barPlot = drawBarPlot(div_obj.id,
                                options,
                                data,
                                type = 'bar',
                                width = null,
                                height = null,
                                callback = callback);
      div_obj.style.height = '400px';
  });
}

function displayPredictionsAnalysis(train_test) {
  return function (selected_bar) {
    var index = selected_bar[0]._index;
    var query = buildQuery('predictionsAnalysis',
                           [project, dataset, experiment_id, train_test, index]);
    window.open(query);
  }
}
