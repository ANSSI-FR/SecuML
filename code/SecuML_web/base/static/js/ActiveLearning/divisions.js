function generateDivisions(conf) {
  generateFirstRowDivisions(conf);
  generateSecondRowDivisions(conf);
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
  var check_annotations_div = createPanel('panel-info', null, 'Check Annotations', iteration_info_col);
  check_annotations_div.id = 'check_annotations';

  // Evolution monitoring
  var evolution_monitoring = createPanel('panel-primary', 'col-md-3', 'Evolution Monitoring', main);
  createDivWithClass('evolution_monitoring', 'tabbable boxed parentTabs', evolution_monitoring);

  // Coefficient interpretation (only if available)
  if (conf.classification_conf) {
    if (conf.classification_conf.feature_coefficients) {
      var model_coefficients = createPanel('panel-primary', 'col-md-4', 'Model Coefficients', main);
      model_coefficients.setAttribute('id', 'model_coefficients');
    }
  }
}

function generateSecondRowDivisions(conf) {
  var row = $('#row_3')[0];
  var col_size = 'col-md-4';
  if (conf.classification_conf) {
    // Train, test and validation monitoring
    createTrainTestMonitoring('train', col_size, row);
    createTrainTestMonitoring('test', col_size, row);
    if (conf.validation_conf) {
      createTrainTestMonitoring('validation', col_size, row);
    }
  }
}
