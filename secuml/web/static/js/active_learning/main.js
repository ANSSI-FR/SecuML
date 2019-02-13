var path   = window.location.pathname.split('/');
var exp_id = path[2];
var view   = path[3];

if (view == '') {
    view = 'ml';
}

var exp_type          = 'ActiveLearning';
var monitorings       = null;
var current_iteration = null;
var classifier_conf   = null;

function callback(conf) {
    conf.query_strategy = conf.core_conf.__type__.split('Conf')[0];
    conf.has_ground_truth = conf.dataset_conf.has_ground_truth;
    conf.validation_has_ground_truth = null;
    var validation_conf = conf.core_conf.validation_conf;
    if (validation_conf) {
        conf.validation_has_ground_truth = hasGroundTruth(
                                            conf.dataset_conf.project,
                                            validation_conf.test_dataset);
    }
    classifier_conf = conf.core_conf.main_model_conf.classifier_conf;
    generateDivisions(conf);
    displayIterations(conf)();
    // Update the display every 10s
    window.setInterval(displayIterations(conf), 10000);
}


loadConfigurationFile(exp_id, callback);

function displayIteration(conf) {
  var iteration = getIteration();
  displayLabelsInformation(exp_id, iteration);
  updateEvolutionMonitoringDisplay(conf, iteration);
  displayAnnotationQueries(conf, iteration);
  if (view == 'ml') {
    if (classifier_conf) {
        d3.json(buildQuery('getIterMainModelConf', [conf.exp_id, iteration]),
            function(data) {
                var sup_exp_conf = data;
                children_exps = {};
                for (var i in monitorings) {
                  displayMonitoring(sup_exp_conf, monitorings[i], 'None');
                }
            });
    }
  }
}

function displayIterations(conf) {
  return function() {
    var current_iteration_db = currentAnnotationIteration(conf.exp_id);
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
