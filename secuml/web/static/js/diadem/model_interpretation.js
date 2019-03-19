function displayModelInterpretation(conf, fold_id, child_type) {
    d3.json(buildQuery('getDiademTrainChildExp',
                       [conf.exp_id, fold_id, child_type]),
            function(exp_info) {
                if (exp_info.model_interp) {
                    displayCoefficientsDiv(exp_info.exp_id);
                    displayCoefficients(exp_info.exp_id);
                }
            });
}

function displayCoefficientsDiv(child_exp_id) {
  if (classifier_conf.feature_importance == 'weight') {
      var title = 'Model Coefficients';
  } else if (classifier_conf.feature_importance == 'score') {
      var title = 'Features Importance';
  }
  var div = cleanDiv('coeff');
  var model_coefficients = createPanel('panel-primary', null, title, div);
  model_coefficients.setAttribute('id', 'model_coefficients');
}

function displayCoefficients(train_exp) {
  var model_coefficients_div = cleanDiv('model_coefficients');
  var query = buildQuery('supervisedLearningMonitoring', [train_exp,
                                                          'coeff_barplot']);
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data);
      barPlotAddTooltips(options, data.tooltip_data);
      barPlotAddBands(options, true);
      options.legend.display = false;
      var barPlot = drawBarPlot('model_coefficients',
              options,
              data,
              type = 'horizontalBar',
              width = null,
              height = '400px',
              callback = getCoefficientsCallback(train_exp));
  });
}
