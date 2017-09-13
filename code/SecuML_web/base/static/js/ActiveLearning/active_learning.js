var path = window.location.pathname.split('/');
var experiment_id = path[2];
var view          = path[3];

if (view == '') {
    view = 'ml';
}

var exp_type          = 'ActiveLearning';
var monitorings       = null;
var current_iteration = null;

loadConfigurationFile(experiment_id, callback);

function loadConfigurationFile(experiment_id, callback) {
  d3.json(buildQuery('getConf', [experiment_id]),
          function(error, data) {
              var conf = data;
              if (conf['conf']['validation_conf']) {
                  conf['validation_has_true_labels'] = hasTrueLabels(
                                   conf['conf']['validation_conf']['test_exp']['experiment_id']);
              }
              if (conf.conf.models_conf['binary']) {
                  conf.classification_conf = conf.conf.models_conf['binary'];
              } else if (conf.conf.models_conf['multiclass']) {
                  conf.classification_conf = conf.conf.models_conf['multiclass'];
              }
              callback(conf);
           }
          );
}

function displayIteration(conf) {
  var iteration = getIteration();
  displayLabelsInformation(experiment_id, iteration);
  updateEvolutionMonitoringDisplay(conf, iteration);
  displayAnnotationQueries(conf, iteration);
  if (view == 'ml') {
    if (conf.classification_conf) {
        var sup_exp = getIterationSupervisedExperiment(conf, iteration);
        displayIterationModelCoefficients(conf, sup_exp);
        for (var i in monitorings) {
          updateMonitoringDisplay(conf, monitorings[i], sup_exp);
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
