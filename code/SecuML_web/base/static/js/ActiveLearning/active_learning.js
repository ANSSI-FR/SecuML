var project         = window.location.pathname.split('/')[2];
var dataset         = window.location.pathname.split('/')[3];
var experiment_id   = window.location.pathname.split('/')[4];

var exp_type = 'ActiveLearning';

loadConfigurationFile(project, dataset, experiment_id, callback);

function loadConfigurationFile(project, dataset, experiment_id, callback) {
  d3.json(buildQuery('getConf', [project, dataset, experiment_id]),
          function(error, data) {
              var conf = data;
              if (conf['validation_conf']) {
                  conf['validation_has_true_labels'] = hasTrueLabels(project, conf['validation_conf']['test_dataset']);
              }
              callback(conf);
           }
          );
}

function displayIteration(conf) {
  var iteration = getIteration();
  displayLabelsInformation(project, dataset, experiment_id, iteration);
  updateEvolutionMonitoringDisplay(conf, iteration);
  displayAnnotationQueries(conf, iteration);
  if (conf.classification_conf) {
      var sup_exp = getBinarySupervisedExperiment(conf, iteration);
      displayIterationModelCoefficients(conf, sup_exp);
      updateMonitoringDisplay(conf, 'train', sup_exp);
      updateMonitoringDisplay(conf, 'test', sup_exp);
      if (conf.validation_conf) {
        updateMonitoringDisplay(conf, 'validation', sup_exp);
      }
  }
}

function callback(conf) {
  generateDivisions(conf);
  displaySettings(conf);
  displayIterationSelector(conf);
  if (conf.classification_conf) {
      displayMonitoringTabs(conf, 'train');
      displayMonitoringTabs(conf, 'test');
      if (conf.validation_conf) {
        displayMonitoringTabs(conf, 'validation');
      }
  }
  displayEvolutionMonitoringTabs(conf);
  displayIteration(conf);
}
