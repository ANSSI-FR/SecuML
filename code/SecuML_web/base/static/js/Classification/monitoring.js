var num_coeff = 20;

function createTrainTestMonitoring(train_test, col_size, parent_div) {
  var monitoring = createPanel('panel-primary', col_size, upperCaseFirst(train_test), parent_div);
  createDivWithClass(train_test + '_monitoring', 'tabbable boxed parentTabs', monitoring);
}

function displayAlertsButton(buttons_group, button_label, buttons_title) {
  var label_group = createDivWithClass(null, 'btn-group', parent_div = buttons_group);
  var label_button = document.createElement('button');
  label_button.setAttribute('class', 'btn btn-danger');
  label_button.setAttribute('type', 'button');
  label_button.setAttribute('id', button_label + '_button');
  var label_button_text = document.createTextNode(buttons_title);
  label_button.appendChild(label_button_text);
  label_button.addEventListener('click', function() {
    if (button_label != 'clustering') {
      var query = buildQuery('alerts',
                             [project, dataset, experiment_id, button_label]);
    } else {
      var validation_project = project;
      var validation_dataset = getValidationDataset(project, dataset,
                      experiment_id);
      var clustering_experiment_id = getAlertsClusteringExperimentId(
                      project, dataset, experiment_id);
      var query = buildQuery('SecuML',
                              [validation_project, validation_dataset,
                              clustering_experiment_id]);
    }
    window.open(query);
  });
  label_group.appendChild(label_button);
}

function displayAlertsButtons() {
  var test_monitoring = document.getElementById('test_monitoring');
  var alerts_div = createPanel('panel-danger', null, 'Alerts Analysis', test_monitoring);
  var buttons_group = createDivWithClass(null, 'btn-group btn-group-justified', parent_div = alerts_div);
  var labels = ['topN', 'random', 'clustering'];
  var titles = ['Top N', 'Random', 'Clustering'];
  for (var i = 0; i < labels.length; i++) {
    displayAlertsButton(buttons_group, labels[i], titles[i]);
  }
}

function validationWithoutTrueLabels(train_test, conf, exp_type) {
    if (exp_type == 'Classification') {
      return train_test == 'test' && !conf.validation_has_true_labels;
    } else if (exp_type == 'ActiveLearning') {
      return (train_test == 'test' && !conf.has_true_labels) || (train_test == 'validation' & !conf.validation_has_true_labels);
    }
}

function displayMonitoring(conf, train_test) {
  if (train_test == 'train' && exp_type == 'Classification') {
    displayCoefficients(conf);
  }
  displayMonitoringTabs(conf, train_test);
  updateMonitoringDisplay(conf, train_test);
}

function updateMonitoringDisplay(conf, train_test, sup_exp = null) {
  updatePredictionsDisplay(conf, train_test, sup_exp);
  var no_true_labels = validationWithoutTrueLabels(train_test, conf,
          exp_type);
  if (! no_true_labels) {
      updatePerformanceDisplay(conf, train_test, sup_exp);
  }
}

function displayMonitoringTabs(conf, train_test) {
  var tabs_div = document.getElementById(train_test + '_monitoring');;
  var no_true_labels = validationWithoutTrueLabels(train_test, conf,
          exp_type);
  var menu_titles = [];
  var menu_labels = [];
  if (! no_true_labels) {
      var menu_titles = ['Performance'];
      var menu_labels = [train_test + '_performance'];
  }
  var probabilist_model = conf.classification_conf.probabilist_model;
  if (probabilist_model) {
    menu_titles.push('Predictions');
    menu_labels.push(train_test + '_predictions');
  }

  var menu = createTabsMenu(menu_labels, menu_titles,
          tabs_div, train_test + '_monitoring_tabs');
  if (! no_true_labels) {
      displayPerformanceTabs(conf, train_test);
  }
}

function displayCoefficients(conf, sup_exp = null) {
  if (! conf.classification_conf.feature_coefficients) {
      return;
  }
  var exp = conf.experiment_id;
  if (sup_exp) {
    exp = sup_exp;
  }
  var model_coefficients_div = cleanDiv('model_coefficients');
  var query = buildQuery('getTopModelCoefficients',
    [conf.project, conf.dataset, exp, num_coeff]);
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data);
      options.legend.display = false;
      var barPlot = drawBarPlot('model_coefficients',
                                 options, data, 'horizontalBar');
      model_coefficients_div.style.height = '400px';
      model_coefficients_div.style.width = '500px';
  });
}
