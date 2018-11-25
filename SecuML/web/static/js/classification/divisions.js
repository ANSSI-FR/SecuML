function generateDivisions(conf) {
  generateTitle('Classification - ' + classifier_conf.model_class_name);

  var main = $('#main')[0];

  // Experiment
  var experiment_row = createDivWithClass(null, 'row', main);
  var experiment = createExperimentDiv('col-md-4', experiment_row);

  // Monitoring row
  var row = createDivWithClass('monitoring_row', 'row', main);

  var test_method = test_conf.method
  if (['cv', 'temporal_cv', 'sliding_window'].indexOf(test_method) > -1) {
    displayFoldIdSelectList(conf, experiment_row);
    displayMonitoringRow(conf, 'all');
  } else {
    displayMonitoringRow(conf);
  }
}

function displayFoldIdMonitoring(conf) {
    return function() {
        var fold_id_select = document.getElementById('fold_id_select')
        var selected_fold = getSelectedOption(fold_id_select);
        displayMonitoringRow(conf, selected_fold);
    }
}

function displayFoldIdSelectList(conf, experiment_row) {
  var num_folds = test_conf.num_folds;
  var select_fold_div = createDivWithClass(null, 'col-md-2', experiment_row);
  var fold_id_select = createSelectList('fold_id_select', 1,
                                        displayFoldIdMonitoring(conf),
                                        select_fold_div,
                                        'Select a fold');
  var elem_list = [];
  var test_method = test_conf.method
  if (['cv', 'temporal_cv', 'sliding_window'].indexOf(test_method) > -1) {
      elem_list.push('all');
  }
  for (var i = 0; i < num_folds; i++) {
      elem_list.push(i);
  }
  addElementsToSelectList('fold_id_select', elem_list);
}

function displayMonitoringRow(conf, selected_fold) {
  var col_size = 'col-md-4';
  var row = cleanDiv('monitoring_row');
  // Row for model coefficients and train/test monitoring
  displayCoefficientsDiv('train', exp_type, conf, row);

  if (!selected_fold) {
    selected_fold = 'None';
  }

  if (selected_fold == 'all') {
    createTrainTestMonitoring('cv', col_size, row);
    displayMonitoring(conf, 'cv', selected_fold);
  } else {
    createTrainTestMonitoring('train', col_size, row);
    createTrainTestMonitoring('test', col_size, row);
    displayMonitoring(conf, 'train', selected_fold);
    displayMonitoring(conf, 'test', selected_fold);
  }

  if (checkDisplayAlerts(conf)) {
    displayAlertsButtons(selected_fold);
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
