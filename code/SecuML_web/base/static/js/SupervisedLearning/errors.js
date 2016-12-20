var tooltip = d3.select('body').append('div')
.attr('class', 'tooltip')
.style('opacity', 0);

var project             = window.location.pathname.split('/')[2];
var dataset             = window.location.pathname.split('/')[3];
var experiment_id       = window.location.pathname.split('/')[4];
var label_iteration     = window.location.pathname.split('/')[5];
var train_test          = window.location.pathname.split('/')[6];
var experiment_label_id = window.location.pathname.split('/')[7];

var args = [project, dataset, experiment_id, label_iteration, train_test];
var hide_confidential = false;
var label_method = 'confusion_matrix';

var last_instance_selector = null;
var last_sublabel = {'malicious': 'other', 'benign': 'other'};
var last_instance_selector = null;

if (train_test == 'train') {
  inst_dataset = dataset;
  inst_exp_id = experiment_id;
  inst_exp_label_id = experiment_label_id;
  callback();
} else {
  setInstancesSettings(project, dataset, experiment_id, experiment_label_id,
          callback);
}

function callback() {
  displayInstanceInformationStructure();
  displayErrors(args);
  displayAnnotationDiv();
}

function displayErrors(args) {
 var query = buildQuery('getErrors', args);
 var query_data;
 d3.json(query, function(error, data) {
      addElementsToSelectList('fp_selector', Object.keys(data['FP']));
      addElementsToSelectList('fn_selector', Object.keys(data['FN']));
      query_data = data;
  });
  var fp_selector = $('#fp_selector')[0];
  fp_selector.addEventListener('change', function() {
      selected_instance_id = getSelectedOption(this);
      printInstanceInformation(selected_instance_id, query_data['FP'][selected_instance_id]);
  });
  var fn_selector = $('#fn_selector')[0];
  fn_selector.addEventListener('change', function() {
      selected_instance_id = getSelectedOption(this);
      printInstanceInformation(selected_instance_id, query_data['FN'][selected_instance_id]);
  });
}
