var project         = window.location.pathname.split('/')[2];
var dataset         = window.location.pathname.split('/')[3];
var experiment_id   = window.location.pathname.split('/')[4];

var hide_confidential = false;

var exp_type = 'ActiveLearning';
var args = [project, dataset, experiment_id];

loadConfigurationFile(project, dataset, experiment_id, callback);

function loadConfigurationFile(project, dataset, experiment_id, callback) {
  d3.json(buildQuery('getConf', args), function(error, data) {
    var conf = data;
    if (conf['validation_conf']) {
        conf['validation_has_true_labels'] = hasTrueLabels(project, conf['validation_conf']['test_dataset']);
    }
    callback(conf);
  });
}

function displayIteration(args, conf) {
  var iteration = getIteration();
  displayLabelsInformation(args, iteration);
  displayTraining(args, iteration, conf);
  displayTesting(args, iteration, conf);
  if (conf.validation_conf) {
    displayValidation(args, iteration, conf);
  }
  displayActiveLearningMonitoring(args, conf);
}

function callback(conf) {
  generateDivisions(conf);
  addCheckLabelsButton(project, dataset, getExperimentLabelId(project, dataset, experiment_id));
  displaySettings(conf);
  displayIterationSelector(args, conf);
  displayMonitoringRadioButtons(args, conf, 'train');
  displayMonitoringRadioButtons(args, conf, 'test');
  if (conf.validation_conf) {
      displayMonitoringRadioButtons(args, conf, 'validation');
  }
  displayEvolutionMonitoringRadioButtons(args, conf);
}
