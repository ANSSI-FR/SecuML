function displayPredictionsBarplot(div, child_exp_id, bar_callback, with_links,
                                   end_callback=null) {
  var div_obj = cleanDiv(div);
  var query = buildQuery('supervisedLearningMonitoring',
                         [child_exp_id, 'pred_barplot']);
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data);
      var barPlot = drawBarPlot(div_obj.id, options, data, type='bar',
                                width=null, height=null);
      var xlabels = barPlot[1].chart.config.data.labels;
      if (with_links) {
        addCallbackToBarplot(barPlot[0], barPlot[1],
                             bar_callback(child_exp_id, xlabels));
      }
      div_obj.style.height = '400px';
      if (end_callback) {
          end_callback(xlabels);
      }
  });
}

function displayPredictionsAnalysis(exp_id, xlabels) {
      return function (selected_bar) {
        var index = selected_bar[0]._index;
        var query = buildQuery('predictionsAnalysis', [exp_id, index]);
        window.open(query);
      }
}

function barPlotCallback(exp_id, xlabels) {
  return function updateDisplay(selected_bar) {
      selected_index = selected_bar[0]._index;
      displayNavigationPanel(selected_index, xlabels);
      updateInstancesDisplay(exp_id, selected_index, null, xlabels);
  }
}
