function displayPredictionsBarplot(div, child_exp_id, callback) {
  var div_obj = cleanDiv(div);
  var query = buildQuery('supervisedLearningMonitoring',
                         [child_exp_id, 'predictions_barplot']);
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

function displayPredictionsAnalysis(exp_id) {
      return function (selected_bar) {
        var index = selected_bar[0]._index;
        var query = buildQuery('predictionsAnalysis', [exp_id, index]);
        window.open(query);
      }
}

function barPlotCallback(exp_id) {
  return function updateDisplay(selected_bar) {
      selected_index = selected_bar[0]._index;
      displayNavigationPanel(selected_index);
      updateInstancesDisplay(exp_id, selected_index);
  }
}
