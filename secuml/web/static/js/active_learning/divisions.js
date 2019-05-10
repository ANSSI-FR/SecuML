function generateDivisions(conf) {
  generateTitle('Active Learning - ' + conf.query_strategy);
  generateFirstRowDivisions(conf);
  monitorings = getClassifMonitoringTab(conf);
  displayEvolutionMonitoringTabs(conf);
}

function generateFirstRowDivisions(conf) {
  createExperimentDiv(null, $('#exp')[0]);
  // Iteration Selector
  var iteration_selector_panel = createPanel('panel-primary', null,
                                             'Select an Iteration',
                                             $('#iter_select_col')[0]);
  var iteration_selector_col = createDivWithClass('iteration_selector_col',
                                         'col-md-4',
                                         parent_div=iteration_selector_panel);
  var iteration_selector = createSelectList('iteration_selector', 5, null,
      iteration_selector_col, label='Iterations');
  var predicted_labels = createDiv('predicted_labels',
                                   parent_div=iteration_selector_col);
  var iteration_info_col = createDivWithClass('iteration_info_col', 'col-md-8',
                                          parent_div=iteration_selector_panel);
  var stats_div = createPanel('panel-info', null, 'Annotation Progress',
                              iteration_info_col);
  stats_div.id = 'stats';
  var check_annotations_div = createDiv('check_annotations',
                                        parent_div=iteration_info_col,
                                        title=null);
  var edit_families_div = createDiv('edit_families',
                                    parent_div=iteration_info_col,
                                    title=null);

  // Evolution monitoring
  var evolution_monitoring = createPanel('panel-primary', null,
                                         'Evolution Monitoring',
                                         $('#monitoring')[0]);
  createDivWithClass('evolution_monitoring', 'tabbable boxed parentTabs',
                     evolution_monitoring);
}

function getClassifMonitoringTab(conf) {
  var monitorings = ['train', 'test'];
  if (conf.core_conf.validation_conf) {
      monitorings.push('validation');
  }
  var row = $('#diadem_monitoring')[0];
  var col_size = 'col-md-4';
  for (var i in monitorings) {
      createDivWithClass(monitorings[i], col_size, parent_div=row);
  }
  return monitorings;
}
