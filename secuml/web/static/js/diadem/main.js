var path = window.location.pathname.split('/');
var exp_id = path[2];
var exp_type = 'Classification';

var conf = null;
var classifier_conf = null;
var test_conf = null;

var children_exps = {}

function callback_1(conf) {
  var classification_conf = conf.core_conf;
  test_conf = classification_conf.test_conf;
  conf.exp_type = exp_type;
  getClassifierConf(conf, classification_conf);
}

function callback_2(conf) {
  generateDivisions(conf);
  displaySettings(conf);
  window.iteration = 'None';
}

loadConfigurationFile(exp_id, callback_1);

function getClassifierConf(conf, classification_conf) {
    var _classifier_conf = classification_conf.classifier_conf;
    if (_classifier_conf.model_class_name != 'AlreadyTrained') {
        classifier_conf = _classifier_conf
        callback_2(conf);
    } else {
        var model_exp_id = _classifier_conf.model_exp_id;
        d3.json(buildQuery('getConf', [model_exp_id]),
                function(data) {
                  classifier_conf = data.core_conf.classifier_conf;
                  callback_2(conf);
        });
    }
}

function displaySettings(conf) {
  var body = createTable('settings', ['', ''], width = 'width:280px');

  // Project Dataset
  addRow(body, ['Project', conf.dataset_conf.project]);
  addRow(body, ['Dataset', conf.dataset_conf.dataset]);

  // Classification
  addRow(body, ['Model Class', classifier_conf.model_class_name]);
}
