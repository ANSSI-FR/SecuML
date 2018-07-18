function generateDivisions(conf) {
  generateTitle(conf);
  generateFirstRowDivisions(conf);
  if (view == 'ml') {
    generateSecondRowDivisions(conf);
  }
  generateTabs(conf);
}

function generateTitle(conf) {
  var main = $('#row_title')[0];
  var div = createDivWithClass(null, 'page-header', parent_div = main);
  var h1 = document.createElement('h1');
  h1.textContent = 'Active Learning - ' + conf.query_strategy;
  div.appendChild(h1);
}

function generateFirstRowDivisions(conf) {
  var main = $('#row_2')[0];
  // Iteration Selector
  var col = createDivWithClass(null, 'col-md-4', parent_div = main);

  var experiment = createExperimentDiv('row', col);

  var iteration_selector_panel = createPanel('panel-primary', 'row', 'Select an Iteration', col);
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
    displayCoefficientsDiv('train', 'ActiveLearning', conf, main);
  }
}

function checkDisplayValidation(conf) {
    if (conf.conf.validation_conf) {
        if (conf.validation_has_ground_truth) {
            return true;
        }
        var multilabel        = conf.classification_conf.families_supervision;
        var probabilist_model = conf.classification_conf.probabilist_model;
        if (probabilist_model && !multilabel) {
            return true;
        }
    }
    return false;
}

function generateSecondRowDivisions(conf) {
  var row = $('#row_3')[0];
  var col_size = 'col-md-4';
  if (checkDisplayValidation(conf)) {
    monitorings = ['train', 'test', 'validation'];
  } else {
    if (conf.query_strategy == 'Gornitz') {
        monitorings = ['train', 'test'];
    } else {
        monitorings = ['train', 'cv', 'test'];
    }
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

function displayCoefficientsDiv(train_test, exp_type, conf, parent_div) {
  if (!conf.classification_conf) {
      return;
  }
  var col_size = 'col-md-4';
  if (checkDisplayCoefficients(train_test, exp_type, conf)) {
    if (conf.classification_conf.feature_importance == 'weight') {
        var title = 'Model Coefficients';
    } else if (conf.classification_conf.feature_importance == 'score') {
        var title = 'Features Importance';
    }
    var model_coefficients = createPanel('panel-primary', col_size, title, parent_div);
    model_coefficients.setAttribute('id', 'model_coefficients');
  }
}
