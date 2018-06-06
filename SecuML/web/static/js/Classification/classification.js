var path = window.location.pathname.split('/');
var experiment_id = path[2];

var exp_type = 'Classification';

loadConfigurationFile(experiment_id, callback);

function loadConfigurationFile(experiment_id, callback) {
  $.getJSON(buildQuery('getConf', [experiment_id]),
            function(data) {
                var conf = data;
                console.log(conf);
                if (conf.classification_conf.test_conf.method == 'dataset') {
                    var test_dataset = conf.classification_conf.test_conf.test_dataset;
                    var validation_exp = getTestExperimentId(conf.experiment_id);
                    conf.validation_has_ground_truth = hasGroundTruth(validation_exp);
                } else {
                    conf.validation_has_ground_truth = conf.has_ground_truth;
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
}
