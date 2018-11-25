var path = window.location.pathname.split('/');
var experiment_id = path[2];
var view          = path[3];

if (view == '') {
    view = 'ml';
}

var exp_type          = 'ActiveLearning';
var monitorings       = null;
var current_iteration = null;
var classifier_conf   = null;

loadConfigurationFile(experiment_id, callback);

function loadConfigurationFile(experiment_id, callback) {
  d3.json(buildQuery('getConf', [experiment_id]),
    function(error, data) {
      var conf = data;
      conf.query_strategy = conf.core_conf.__type__.split('Conf')[0];
      conf.has_ground_truth = conf.dataset_conf.has_ground_truth;
      conf.validation_has_ground_truth = null;
      if (conf.core_conf.validation_conf) {
          var test_dataset_conf = conf.test_exp_conf.dataset_conf;
          conf.validation_has_ground_truth = test_dataset_conf.has_ground_truth;
          conf.validation_exp_id = conf.test_exp_conf.experiment_id;
      }
      if (conf.core_conf.models_conf['binary']) {
          classifier_conf = conf.core_conf.models_conf['binary'].classifier_conf;
      } else if (conf.core_conf.models_conf['multiclass']) {
          classifier_conf = conf.core_conf.models_conf['multiclass'].classifier_conf;
      }
      callback(conf);
    });
}

function displayIteration(conf) {
  var iteration = getIteration();
  displayLabelsInformation(experiment_id, iteration);
  updateEvolutionMonitoringDisplay(conf, iteration);
  displayAnnotationQueries(conf, iteration);
  if (view == 'ml') {
    if (classifier_conf) {
        var sup_exp = getIterationSupervisedExperiment(conf, iteration);
        if (checkDisplayCoefficients('train', 'ActiveLearning', conf)) {
          displayIterationModelCoefficients(conf, sup_exp);
        }
        for (var i in monitorings) {
          updateMonitoringDisplay(conf, monitorings[i], sup_exp, 'None');
        }
    }
  }
}

function callback(conf) {
  generateDivisions(conf);
  displaySettings(conf);
  displayIterations(conf)();
  // Update the display every 10s
  window.setInterval(displayIterations(conf), 10000);
}

function displayIterations(conf) {
  return function() {
    var current_iteration_db = currentAnnotationIteration(conf.experiment_id);
    if (!current_iteration) {
        current_iteration = current_iteration_db;
    } else {
        if (current_iteration == current_iteration_db) {
            // Do not need to update the display
            return;
        } else {
            current_iteration = current_iteration_db;
        }
    }
    displayIterationSelector(conf, current_iteration);
    displayIteration(conf);
  }
}
