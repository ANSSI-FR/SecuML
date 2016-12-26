function generateDivisions(conf) {
  generateFirstRowDivisions(conf);
  generateSecondRowDivisions();
}

function generateFirstRowDivisions(conf) {
  var row = $('#row_1')[0];
  if (conf.validation_conf) {
    var col_size = 'col-md-3' ;
  } else {
    var col_size = 'col-md-4' ;
  }
  // First column: settings and iteration selector
  var first_col = createDivWithClass('first_col', col_size, parent_div = row);
  var settings_row = createDivWithClass('settings_row', 'col-md-12', 
      parent_div = first_col, title = 'Settings');
  var settings_div = createDiv('settings', parent_div = settings_row);
  var labels_row = createDivWithClass('labels_row', 'row', parent_div = first_col);
  var labels_col = createDivWithClass('labels_col', 'col-md-12', parent_div = labels_row);
  var labels_div = createDiv('check_labels_div', parent_div = labels_col);
  var iteration_row = createDivWithClass('iteration_row', 'row', parent_div = first_col);
  var iteration_selector_col = createDivWithClass('iteration_selector_col', 'col-md-4',
      parent_div = iteration_row, title = 'Iterations');
  var iteration_selector = createSelectList('iteration_selector', 5, null,
      parent_div = iteration_selector_col);
  var iteration_info_col = createDivWithClass('iteration_info_col', 'col-md-8',
      parent_div = iteration_row);
  var labels_stats_div = createDiv('labels_stats', parent_div = iteration_info_col);
  var stats_div = createDiv('stats', parent_div = iteration_info_col);
  // Second column: training monitoring
  var second_col = createDivWithClass('second_col', col_size, parent_div = row,
      title = 'Training');
  var radio_div = createDiv('train_radio_monitoring', parent_div = second_col);
  var monitoring_div = createDiv('train_monitoring', parent_div = second_col);
  // Third column: testing monitoring
  var third_col = createDivWithClass('third_col', col_size,
      parent_div = row, titile = 'Testing');
  var radio_div = createDiv('test_radio_monitoring', parent_div = third_col);
  var monitoring_div = createDiv('test_monitoring', parent_div = third_col);
  // [optional] Fourth column: validation monitoring
  if (conf.validation_conf) {
    var fourth_col = createDivWithClass('fourth_col', col_size,
        parent_div = row, title = 'Validation');
    var radio_div = createDiv('validation_radio_monitoring', parent_div = fourth_col);
    var monitoring_div = createDiv('validation_monitoring', parent_div = fourth_col);
  }
}

function generateSecondRowDivisions() {
  var row = $('#row_2')[0];
  var col_size = 'col-md-3' ;
  // First column: labeling monitoring
  var first_col = createDivWithClass('first_col', col_size,
      parent_div = row, titile = '  ');
  var radio_div = createDiv('labeling_radio_monitoring', parent_div = first_col);
  var monitoring_div = createDiv('labeling_monitoring', parent_div = first_col);
  // Second column: evolution monitoring
  var evolution_monitoring_col = createDivWithClass('evolution_monitoring_col', col_size,
      parent_div = row, title = 'Evolution Monitoring');
  var evolution_monitoring = createDiv('evolution_monitoring',
      parent_div = evolution_monitoring_col)
  // Third column: provision labels analysis
  var predicted_labels_col = createDivWithClass('predicted_labels_col', col_size,
      parent_div = row, title = '  ');
  var predicted_labels = createDiv('predicted_labels', 
      parent_div = predicted_labels_col);
}
