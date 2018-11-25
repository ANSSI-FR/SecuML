function generateDivisions(conf) {
  generateTitle('Active Learning - ' + conf.query_strategy);
  generateFirstRowDivisions(conf);
  if (view == 'ml') {
    generateSecondRowDivisions(conf);
  }
  generateTabs(conf);
}

function generateFirstRowDivisions(conf) {
  var main = $('#row_2')[0];
  // Iteration Selector
  var col = createDivWithClass(null, 'col-md-4', parent_div = main);

  var experiment = createExperimentDiv('row', col);

  var iteration_selector_panel = createPanel('panel-primary', 'row',
                                             'Select an Iteration', col);
  var iteration_selector_col = createDivWithClass('iteration_selector_col',
                                         'col-md-4',
                                         parent_div = iteration_selector_panel);
  var iteration_selector = createSelectList('iteration_selector', 5, null,
      iteration_selector_col, label = 'Iterations');
  var predicted_labels = createDiv('predicted_labels',
      parent_div = iteration_selector_col);
  var iteration_info_col = createDivWithClass('iteration_info_col', 'col-md-8',
      parent_div = iteration_selector_panel);
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
  var col_size = 'col-md-4';
  var evolution_monitoring = createPanel('panel-primary', col_size,
                                         'Evolution Monitoring', main);
  createDivWithClass('evolution_monitoring', 'tabbable boxed parentTabs',
                     evolution_monitoring);

  // Coefficient interpretation (only if available)
  if (view == 'ml') {
    displayCoefficientsDiv('train', 'ActiveLearning', conf, main);
  }
}

function checkDisplayValidation(conf) {
    if (conf.core_conf.validation_conf) {
        if (conf.validation_has_ground_truth) {
            return true;
        }
        var multilabel        = classifier_conf.families_supervision;
        var probabilist_model = classifier_conf.probabilist_model;
        if (probabilist_model && !multilabel) {
            return true;
        }
    }
    return false;
}


function getClassifMonitoringTab(conf) {
  if (conf.query_strategy == 'RareCategoryDetection') {
    return [];
  }
  if (checkDisplayValidation(conf)) {
    return ['train', 'test', 'validation'];
  } else {
    if (conf.query_strategy == 'Gornitz') {
      return ['train', 'test'];
    } else {
      return ['train', 'cv', 'test'];
    }
  }
}

function generateSecondRowDivisions(conf) {
  var row = $('#row_3')[0];
  var col_size = 'col-md-4';
  monitorings = getClassifMonitoringTab(conf);
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

function displayCoefficientsDiv(train_test, exp_type, conf, parent_div) {
  var col_size = 'col-md-4';
  if (checkDisplayCoefficients(train_test, exp_type, conf)) {
    if (classifier_conf.feature_importance == 'weight') {
        var title = 'Model Coefficients';
    } else if (classifier_conf.feature_importance == 'score') {
        var title = 'Features Importance';
    }
    var model_coefficients = createPanel('panel-primary', col_size, title,
                                         parent_div);
    model_coefficients.setAttribute('id', 'model_coefficients');
  }
}
