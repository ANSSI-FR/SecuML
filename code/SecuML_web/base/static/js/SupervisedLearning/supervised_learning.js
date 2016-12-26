var project         = window.location.pathname.split('/')[2];
var dataset         = window.location.pathname.split('/')[3];
var experiment_id   = window.location.pathname.split('/')[4];

var hide_confidential = false;

var exp_type = 'SupervisedLearning';
var args = [project, dataset, experiment_id];

function getIteration() {
  return 'None';
}

loadConfigurationFile(project, dataset, experiment_id, callback);

function loadConfigurationFile(project, dataset, experiment_id, callback) {
  d3.json(buildQuery('getConf', args), function(error, data) {
    var conf = data;
    if (conf.supervised_learning_conf.test_conf.method == 'test_dataset') {
        var test_dataset = conf.supervised_learning_conf.test_conf.test_dataset;
        conf.validation_has_true_labels = hasTrueLabels(project, test_dataset);
    } else {
        conf.validation_has_true_labels = conf.has_true_labels;
    }
    callback(conf);
  });
}

function displaySettings(conf) {
  var table = createTable('settings',
      ['', '']);
  table.setAttribute('style','width:280px');
  // Project Dataset
  var row = table.insertRow(1);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Project';
  var cell = row.insertCell(1);
  cell.innerHTML = project;
  var row = table.insertRow(2);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Dataset';
  var cell = row.insertCell(1);
  cell.innerHTML = dataset;
  if (hide_confidential) {
    cell.innerHTML = '';
  }
  // Supervised Learning
  var supervised_learning_conf = conf.supervised_learning_conf;
  var row = table.insertRow(3);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Model Class';
  var cell = row.insertCell(1);
  cell.innerHTML = supervised_learning_conf['__type__'].split('Configuration')[0];
  var row = table.insertRow(4);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Num folds';
  var cell = row.insertCell(1);
  cell.innerHTML = supervised_learning_conf.num_folds;
  var row = table.insertRow(5);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Sample Weights';
  var cell = row.insertCell(1);
  cell.innerHTML = supervised_learning_conf.sample_weight;
}

function callback(conf) {
  displaySettings(conf);
  displayMonitoringRadioButtons(args, conf, 'train');
  displayMonitoringRadioButtons(args, conf, 'test');
  window.iteration = 'None';
  displayTraining(args, window.iteration, conf);
  displayTesting(args, window.iteration, conf);
  displayAlertsButton();
}
