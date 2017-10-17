var path = window.location.pathname.split('/');
var experiment_id = path[2];

var exp_type = 'Classification';

loadConfigurationFile(experiment_id, callback);

function loadConfigurationFile(experiment_id, callback) {
  $.getJSON(buildQuery('getConf', [experiment_id]),
            function(data) {
                var conf = data;
                if (conf.classification_conf.test_conf.method == 'test_dataset') {
                    var test_dataset = conf.classification_conf.test_conf.test_dataset;
                    var validation_exp = conf.classification_conf.test_conf.test_exp.experiment_id
                    conf.validation_has_true_labels = hasTrueLabels(validation_exp);
                } else {
                    conf.validation_has_true_labels = conf.has_true_labels;
                }
                conf.exp_type = exp_type;
                callback(conf);
            }
           );
}

function displaySettings(conf) {
  var body = createTable('settings', ['', ''], width = 'width:280px');

  // Project Dataset
  addRow(body, ['Project', conf.project]);
  addRow(body, ['Dataset', conf.dataset]);

  // Classification
  var classification_conf = conf.classification_conf;
  var model_class = classification_conf['__type__'].split(
          'Configuration')[0];
  var num_folds = classification_conf.num_folds;
  var sample_weight = classification_conf.sample_weight;
  addRow(body, ['Model Class', model_class]);
  addRow(body, ['Num folds', num_folds]);
  addRow(body, ['Sample Weights', sample_weight]);
}

function callback(conf) {
  generateDivisions(conf);
  displaySettings(conf);
  window.iteration = 'None';
  displayMonitoring(conf, 'train');
  displayMonitoring(conf, 'test');
  if (conf.classification_conf.test_conf.alerts_conf) {
    displayAlertsButtons();
  }
}

function generateDivisions(conf) {
  var main = $('#main')[0];

  // Experiment
  var experiment_row = createDivWithClass(null, 'row', main);
  var experiment = createExperimentDiv('col-md-4', experiment_row);

  // Row for model coefficients and train/test monitoring
  var row = createDivWithClass(null, 'row', main);
  var col_size = 'col-md-4';
  if (conf.classification_conf.feature_importance) {
    if (conf.classification_conf.feature_importance == 'weight') {
        var title = 'Model Coefficients';
    } else if (conf.classification_conf.feature_importance == 'score') {
        var title = 'Feature Importances';
    }
    var model_coefficients = createPanel('panel-primary', col_size, title, row);
    model_coefficients.setAttribute('id', 'model_coefficients');
  }
  createTrainTestMonitoring('train', col_size, row);
  createTrainTestMonitoring('test', col_size, row);
}
