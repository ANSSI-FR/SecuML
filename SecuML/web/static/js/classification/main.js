var path = window.location.pathname.split('/');
var experiment_id = path[2];

var exp_type = 'Classification';

var conf = null;
var classifier_conf = null;
var test_conf = null;

loadConfigurationFile(experiment_id, callback);

function loadConfigurationFile(experiment_id, callback) {
  $.getJSON(buildQuery('getConf', [experiment_id]),
     function(data) {
         conf = data
         var classification_conf = conf.core_conf;
         classifier_conf = classification_conf.classifier_conf;
         test_conf = classification_conf.test_conf;
         var val_dataset_conf = conf.dataset_conf;
         if (test_conf.method == 'dataset') {
             val_dataset_conf = conf.test_exp_conf.dataset_conf;
             conf.validation_exp_id = conf.test_exp_conf.experiment_id;
         }
         conf.validation_has_ground_truth = val_dataset_conf.has_ground_truth;
         conf.exp_type = exp_type;
         conf.has_ground_truth = conf.dataset_conf.has_ground_truth;
         callback(conf);
     }
    );
}

function displaySettings(conf) {
  var body = createTable('settings', ['', ''], width = 'width:280px');

  // Project Dataset
  addRow(body, ['Project', conf.dataset_conf.project]);
  addRow(body, ['Dataset', conf.dataset_conf.dataset]);

  // Classification
  addRow(body, ['Model Class', classifier_conf.model_class_name]);
}

function callback(conf) {
  generateDivisions(conf);
  displaySettings(conf);
  window.iteration = 'None';
}
