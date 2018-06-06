function displayPredictionsBarplot(div, conf, train_test, experiment_id,
                                   fold_id, callback) {
  var div_obj = cleanDiv(div);



  var exp_type = conf.__type__.split('Experiment')[0];
  var query = buildQuery('supervisedLearningMonitoring',
                         [experiment_id, train_test, 'predictions_barplot',
                          fold_id]);
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

function displayPredictionsAnalysis(experiment_id, train_test, fold_id) {
  if (fold_id == 'all') {
      return null;
  } else {
      return function (selected_bar) {
        var index = selected_bar[0]._index;
        var query = buildQuery('predictionsAnalysis',
                               [experiment_id, train_test, fold_id, index]);
        window.open(query);
      }
  }
}

function barPlotCallback(experiment_id) {
  return function updateDisplay(selected_bar) {
      selected_index = selected_bar[0]._index;
      displayNavigationPanel(selected_index);
      updateInstancesDisplay(experiment_id, selected_index);
  }
}
