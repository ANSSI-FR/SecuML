function displayEvolutionMonitoringTabs(conf) {
  var menu_titles = ['Families'];
  var menu_labels = ['families_evolution'];
  if (conf.validation_conf) {
      menu_titles.push('Validation');
      menu_labels.push('validation_evolution');
  }
  menu_titles.push('Time');
  menu_labels.push('time_evolution');
  createTabsMenu(menu_labels, menu_titles, document.getElementById('evolution_monitoring'));
  if (conf.validation_conf) {
      displayValidationEvolutionMonitoringTabs();
  }
}

function updateEvolutionMonitoringDisplay(conf, iteration) {
  displayFamiliesEvolutionMonitoring(conf, iteration);
  if (conf.validation_conf) {
    updateValidationEvolutionMonitoring(conf, iteration);
  }
  displayExecutionTimeEvolutionMonitoring(conf, iteration);
}

function displayClusteringEvolutionTabs() {
  var menu_titles = ['V-measure', 'Homogeneity', 'Completeness'];
  var menu_labels = ['v_measure', 'homogeneity', 'completeness'];
  createTabsMenu(menu_labels, menu_titles,
          document.getElementById('clustering_evolution'),
          'clustering_evolution_tabs');
}

function displayValidationEvolutionMonitoringTabs() {
  var menu_titles = ['AUC', 'F-score'];
  var menu_labels = ['auc', 'fscore'];
  createTabsMenu(menu_labels, menu_titles,
          document.getElementById('validation_evolution'),
          'validation_evolution_tabs');
}

function displayExecutionTimeEvolutionMonitoring(conf, iteration) {
  var time_evolution = cleanDiv('time_evolution');
  var query = buildQuery('activeLearningMonitoring',
                         [conf.project, conf.dataset, conf.experiment_id,
                          iteration, 'time', 'all']);
  var picture = document.createElement('img');
  picture.setAttribute('class', 'img-responsive');
  picture.src = query;
  time_evolution.appendChild(picture);
}

function displayFamiliesEvolutionMonitoring(conf, iteration) {
  var families_evolution = cleanDiv('families_evolution');
  var query = buildQuery('activeLearningMonitoring',
                         [conf.project, conf.dataset, conf.experiment_id,
                          iteration, 'families', 'all']);
  var picture = document.createElement('img');
  picture.setAttribute('class', 'img-responsive');
  picture.src = query;
  families_evolution.appendChild(picture);
}

function updateClusteringEvolutionMonitoring(conf, iteration) {
    var estimators = ['v_measure', 'homogeneity', 'completeness'];
    for (var i in estimators) {
      var estimator = estimators[i];
      var div = cleanDiv(estimator);
      var query = buildQuery('activeLearningMonitoring',
                             [conf.project, conf.dataset, conf.experiment_id,
                              iteration, 'clustering', estimator]);
      var picture = document.createElement('img');
      picture.setAttribute('class', 'img-responsive');
      picture.src = query;
      div.appendChild(picture);
    }
}

function updateValidationEvolutionMonitoring(conf, iteration) {
    var estimators = ['auc', 'fscore'];
    for (var i in estimators) {
      var estimator = estimators[i];
      var div = cleanDiv(estimator);
      var query = buildQuery('activeLearningMonitoring',
                             [conf.project, conf.dataset, conf.experiment_id,
                              iteration, 'validation', estimator]);
      var picture = document.createElement('img');
      picture.setAttribute('class', 'img-responsive');
      picture.src = query;
      div.appendChild(picture);
    }
}

function displayIterationModelCoefficients(conf, sup_exp) {
    displayCoefficients(conf, sup_exp);
}
