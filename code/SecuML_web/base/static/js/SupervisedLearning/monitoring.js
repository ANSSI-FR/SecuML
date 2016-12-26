function displayAlertsButton() {
  var alerts_div = cleanDiv('predictions_labeling');
  var button = document.createElement('button');
  button.appendChild(document.createTextNode('Alerts Analysis'));
  button.addEventListener('click', function() {
      var query = buildQuery('alerts', 
              [project, dataset, experiment_id, iteration]);
      window.open(query);
  });
  alerts_div.appendChild(button);
}

function displayTraining(args, iteration, conf) {
  displayMonitoring(args, iteration, conf, 'train');
}

function displayTesting(args, iteration, conf) {
  displayMonitoring(args, iteration, conf, 'test');
  if (iteration != 'None') {
    displayAnnotationQueries(args, iteration, conf);
  }
}

function displayValidation(args, iteration, conf) {
  displayMonitoring(args, iteration, conf, 'validation');
}

function validationWithoutTrueLabels(train_test, conf, exp_type) {
    if (exp_type == 'SupervisedLearning') {
      return train_test == 'test' && !conf.validation_has_true_labels;
    } else if (exp_type == 'ActiveLearning') {
      return (train_test == 'test' && !conf.has_true_labels) || (train_test == 'validation' & !conf.validation_has_true_labels);
    }
}

function familiesMonitoring(train_test, conf) {
    if (train_test == 'validation') {
        return datasetHasSublabels(conf.project, conf.validation_conf.test_dataset, 1);
    } else {
        return datasetHasSublabels(conf.project, conf.dataset, conf.experiment_label_id);
    }
}

function displayMonitoring(args, iteration, conf, train_test) {
  var div_name = train_test + '_monitoring';
  if (validationWithoutTrueLabels(train_test, conf, exp_type)) {
    displayPredictions(args, iteration, conf, train_test);
  } else {
    var radio_performance = $('#radio_' + train_test + '_performance')[0];
    var radio_predictions = $('#radio_' + train_test + '_predictions')[0];
    var radio_families = $('#radio_' + train_test + '_families')[0];
    if (radio_performance.checked) {
      displayPerformance(args, iteration, train_test);
    } else if (radio_predictions.checked) {
      displayPredictions(args, iteration, conf, train_test);
    } else if (radio_families.checked) {
      displayFamiliesMonitoring(args, iteration, train_test);
    }
  }
}

function displayMonitoringRadioButtons(args, conf, train_test) {
  var div_name = train_test + '_monitoring';
  var radio_name =  train_test + '_radio_monitoring';
  var radio_div = cleanDiv(radio_name);
  if (validationWithoutTrueLabels(train_test, conf, exp_type)) {
    displayPredictionsRadio(div_name, args, conf, train_test);
  } else {
    // Performance
    var radio_performance = makeRadioButton(radio_name,
        train_test + '_performance', 'Performance',
        true, function() {
          var iteration = getIteration();
          displayPerformanceRadio(div_name, args, train_test);
          displayPerformance(args, iteration, train_test);
        },
        parent_div = radio_div);
    displayPerformanceRadio(div_name, args, train_test);
    // Families
    if (familiesMonitoring(train_test, conf)) {
      var radio_families = makeRadioButton(radio_name,
          train_test + '_families', 'Families',
          false, function() {
            var iteration = getIteration();
            displayFamiliesMonitoring(args, iteration, train_test);
          },
          parent_div = radio_div);
    }
    // Predictions
    var radio_predictions = makeRadioButton(radio_name,
        train_test + '_predictions', 'Predictions',
        validationWithoutTrueLabels(train_test, conf, exp_type), 
        function() {
          var iteration = getIteration();
          displayPredictionsRadio(div_name, args, conf, train_test);
          displayPredictions(args, iteration, conf, train_test);
        },
        parent_div = radio_div);
    }
}
