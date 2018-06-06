function generateDivisions(conf) {
  generateTitle(conf);

  var main = $('#main')[0];

  // Experiment
  var experiment_row = createDivWithClass(null, 'row', main);
  var experiment = createExperimentDiv('col-md-4', experiment_row);

  // Monitoring row
  var row = createDivWithClass('monitoring_row', 'row', main);

  if (conf.classification_conf.test_conf.method == 'cv') {
    displayFoldIdSelectList(conf, experiment_row);
    displayMonitoringRow(conf, 'all');
  } else {
    displayMonitoringRow(conf);
  }
}

function generateTitle(conf) {
  var main = $('#row_title')[0];
  var div = createDivWithClass(null, 'page-header', parent_div = main);
  var h1 = document.createElement('h1');
  h1.textContent = 'Classification - ' + conf.classification_conf.model_class;
  div.appendChild(h1);
}

function displayFoldIdMonitoring(conf) {
    return function() {
        var fold_id_select = document.getElementById('fold_id_select')
        var selected_fold = getSelectedOption(fold_id_select);
        displayMonitoringRow(conf, selected_fold);
    }
}

function displayFoldIdSelectList(conf, experiment_row) {
  var num_folds = conf.classification_conf.test_conf.num_folds;
  var select_fold_div = createDivWithClass(null, 'col-md-2', experiment_row);
  var fold_id_select = createSelectList('fold_id_select', 1,
                                        displayFoldIdMonitoring(conf),
                                        select_fold_div,
                                        'Select a fold');
  var elem_list = ['all'];
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
    displayAlertsButtons();
  }
}

function displayCoefficientsDiv(train_test, exp_type, conf, parent_div) {
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
