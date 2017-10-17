function generateDivisions(conf) {
  generateFirstRowDivisions(conf);
  if (view == 'ml') {
    generateSecondRowDivisions(conf);
  }
  generateTabs(conf);
}

function generateFirstRowDivisions(conf) {
  // Experiment
  var main = $('#row_1')[0];
  var experiment = createExperimentDiv('col-md-4', main);

  var main = $('#row_2')[0];
  // Iteration Selector
  var iteration_selector_panel = createPanel('panel-primary', 'col-md-4', 'Select an Iteration', main);
  var iteration_selector_col = createDivWithClass('iteration_selector_col', 'col-md-4',
      parent_div = iteration_selector_panel);
  var iteration_selector = createSelectList('iteration_selector', 5, null,
      iteration_selector_col, label = 'Iterations');
  var predicted_labels = createDiv('predicted_labels',
      parent_div = iteration_selector_col);
  var iteration_info_col = createDivWithClass('iteration_info_col', 'col-md-8',
      parent_div = iteration_selector_panel);
  var stats_div = createPanel('panel-info', null, 'Annotation Progress', iteration_info_col);
  stats_div.id = 'stats';
  var check_annotations_div = createDiv('check_annotations', parent_div = iteration_info_col, title = null);
  var edit_families_div = createDiv('edit_families', parent_div = iteration_info_col, title = null);

  // Evolution monitoring
  var col_size = 'col-md-4';
  var evolution_monitoring = createPanel('panel-primary', col_size, 'Evolution Monitoring', main);
  createDivWithClass('evolution_monitoring', 'tabbable boxed parentTabs', evolution_monitoring);

  // Coefficient interpretation (only if available)
  if (view == 'ml') {
    if (conf.classification_conf) {
      if (conf.classification_conf.feature_importance) {
        if (conf.classification_conf.feature_importance == 'weight') {
            var title = 'Model Coefficients';
        } else if (conf.classification_conf.feature_importance == 'score') {
            var title = 'Feature Importances';
        }
        var model_coefficients = createPanel('panel-primary', 'col-md-4', title, main);
        model_coefficients.setAttribute('id', 'model_coefficients');
      }
    }
  }
}

function generateSecondRowDivisions(conf) {
  var row = $('#row_3')[0];
  var col_size = 'col-md-4';
  console.log(conf);
  if (conf.conf.validation_conf) {
    monitorings = ['train', 'test', 'validation'];
  } else {
    monitorings = ['train', 'cv', 'test'];
  }
  for (var i in monitorings) {
    createTrainTestMonitoring(monitorings[i], col_size, row);
  }
}

function generateTabs(conf) {
  displayEvolutionMonitoringTabs(conf);
  for (var i in monitorings) {
    displayMonitoringTabs(conf, monitorings[i]);
  }
}
