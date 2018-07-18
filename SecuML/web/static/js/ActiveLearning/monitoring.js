function displayEvolutionMonitoringTabs(conf) {
  var menu_titles = [];
  var menu_labels = [];
  menu_titles.push('Families');
  menu_labels.push('families_evolution');
  if (view == 'ml') {
    menu_titles.push('Models');
    menu_labels.push('models_evolution');
    menu_titles.push('Time');
    menu_labels.push('time_evolution');
  }
  if (conf.query_strategy == 'Ilab') {
    menu_titles.push('Suggestions');
    menu_labels.push('suggestions_evolution');
  }
  createTabsMenu(menu_labels, menu_titles, document.getElementById('evolution_monitoring'));
  if (view == 'ml') {
    displayModelsEvolutionMonitoringTabs(conf);
  }
}

function updateEvolutionMonitoringDisplay(conf, iteration) {
  updateFamiliesEvolutionMonitoring(conf, iteration);
  updateSuggestionsEvolutionMonitoring(conf, iteration);
  if (view == 'ml') {
    updateModelsEvolutionMonitoring(conf, iteration);
    updateExecutionTimeEvolutionMonitoring(conf, iteration);
  }
}

function displayModelsEvolutionMonitoringTabs(conf) {
  var menu_titles = ['Train'];
  var menu_labels = ['train'];
  if (conf.query_strategy != 'Gornitz') {
    menu_titles.push('Cv');
    menu_labels.push('cv');
  }
  if (conf.conf.validation_conf) {
      if (conf.validation_has_ground_truth) {
        menu_titles.push('Validation');
        menu_labels.push('validation');
      }
  }
  createTabsMenu(menu_labels, menu_titles,
          document.getElementById('models_evolution'),
          'models_evolution_tabs');
    document.getElementById('models_evolution').style.marginTop = '2px';
}

function updateSuggestionsEvolutionMonitoring(conf, iteration) {
    if (conf.query_strategy != 'Ilab') {
        return;
    }
    var suggestions_evolution = cleanDiv('suggestions_evolution');
    if (iteration == 1) {
      suggestions_evolution.appendChild(document.createTextNode(
                  'No estimation of the accuracy of the suggestions at the first iteration.'));
    } else {
      var query = buildQuery('activeLearningSuggestionsMonitoring',
                             [conf.experiment_id,
                              iteration]);
      var picture = document.createElement('img');
      picture.setAttribute('class', 'img-responsive');
      picture.src = query;
      suggestions_evolution.appendChild(picture);
    }
}

function executionTimeEvolutionMonitoringAvailable(time_evolution, picture) {
    return function() {
        time_evolution.appendChild(picture);
    }
}

function executionTimeEvolutionMonitoringUnavailable(time_evolution) {
    return function() {
      time_evolution.appendChild(document.createTextNode(
                  'Execution time monitoring is not available yet.'));
    }
}

function updateExecutionTimeEvolutionMonitoring(conf, iteration) {
  var time_evolution = cleanDiv('time_evolution');
  var query = buildQuery('activeLearningMonitoring',
                         [conf.experiment_id,
                          iteration, 'time', 'all']);
  var picture = document.createElement('img');
  picture.setAttribute('class', 'img-responsive');
  picture.src = query;
  picture.onerror = executionTimeEvolutionMonitoringUnavailable(time_evolution);
  picture.onload = executionTimeEvolutionMonitoringAvailable(time_evolution, picture);
}

function updateFamiliesEvolutionMonitoring(conf, iteration) {
  var families_evolution = cleanDiv('families_evolution');
  var query = buildQuery('activeLearningMonitoring',
                         [conf.experiment_id,
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
                             [conf.experiment_id,
                              iteration, 'clustering', estimator]);
      var picture = document.createElement('img');
      picture.setAttribute('class', 'img-responsive');
      picture.src = query;
      div.appendChild(picture);
    }
}

function updateModelsEvolutionMonitoring(conf, iteration) {
      var types = ['train'];
      if (conf.query_strategy != 'Gornitz') {
        types.push('cv');
      }
      if (conf.conf.validation_conf) {
          if (conf.validation_has_ground_truth) {
            types.push('validation');
          }
      }
      for (var t in types) {
        var type = types[t];
        var div = cleanDiv(type);
        var query = buildQuery('activeLearningModelsMonitoring',
                               [conf.experiment_id,
                                iteration, type]);
        var picture = document.createElement('img');
        picture.setAttribute('class', 'img-responsive');
        picture.src = query;
        div.appendChild(picture);
      }
}

function displayIterationModelCoefficients(conf, sup_exp) {
    displayCoefficients(conf, sup_exp, 'train', 'None');
}
