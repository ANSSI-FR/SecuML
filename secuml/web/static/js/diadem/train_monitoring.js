function displayTrainingMonitoring(conf, fold_id, child_type) {
    d3.json(buildQuery('getDiademTrainChildExp',
                       [conf.exp_id, fold_id, child_type]),
            function(exp_info) {
                if (exp_info.model_interp) {
                    displayModelInterpretation(exp_info.exp_id);
                }
                displayTrainExecTimes(exp_info.exp_id);
            });
}

function displayTrainExecTimes(train_exp) {
    var div = cleanDiv('exec_times');
    var exec_times = createPanel('panel-primary', null,
                                 'Training Execution Times (in seconds)', div);
    exec_times.setAttribute('id', 'train_exec_times');
    var query = buildQuery('supervisedLearningMonitoring', [train_exp,
                                                            'exec_times']);
    $.getJSON(query, function(data) {
        var body = createTable('train_exec_times', ['', '']);
        addRow(body, ['Search for best hyperparameters',
                      data.best_hyper_params.toFixed(9)]);
        addRow(body, ['Training', data.training.toFixed(9)]);
        addRow(body, ['Total',
                      (data.best_hyper_params + data.training).toFixed(9)]);
    });
}

function displayModelInterpretation(train_exp) {
  if (classifier_conf.feature_importance == 'weight') {
      var title = 'Model Coefficients';
  } else if (classifier_conf.feature_importance == 'score') {
      var title = 'Features Importance';
  }
  var div = cleanDiv('coeff');
  if (classifier_conf.multiclass) {
    var class_select = createSelectList('class_select', 3, null,
                                        div, label='Select a family',
                                        multiple=false, with_search=true);
    class_select.addEventListener('change',
                                  function() {
                                    displayCoefficients(train_exp,
                                            getSelectedOption(class_select));
                                  });
    var query = buildQuery('supervisedLearningMonitoring',
                           [train_exp, 'class_labels']);
    $.getJSON(query, function (data) {
        var class_labels = data['class_labels'];
        addElementsToSelectList('class_select', class_labels);
        var model_coefficients = createPanel('panel-primary', null, title,
                                             div);
        model_coefficients.setAttribute('id', 'model_coefficients');
        displayCoefficients(train_exp, class_labels[0]);
    });
  } else {
    var model_coefficients = createPanel('panel-primary', null, title, div);
    model_coefficients.setAttribute('id', 'model_coefficients');
    displayCoefficients(train_exp, 'None');
  }
}

function displayCoefficients(train_exp, class_label) {
  var model_coefficients_div = cleanDiv('model_coefficients');
  var query = buildQuery('modelInterpretation', [train_exp, class_label]);
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
