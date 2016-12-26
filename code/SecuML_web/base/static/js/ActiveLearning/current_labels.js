var project             = window.location.pathname.split('/')[2];
var dataset             = window.location.pathname.split('/')[3];
var experiment_label_id = window.location.pathname.split('/')[4];
var label_iteration     = window.location.pathname.split('/')[5];

var label_method = 'check_label';
var hide_confidential = false;

var args = [project, dataset, experiment_label_id];

var last_sublabel = {'malicious': 'other', 'benign': 'other'};
var last_instance_selector = null;

var inst_dataset = dataset;
var inst_exp_label_id = experiment_label_id;

displayInstanceInformationStructure();
displaySelectors(args);
displayAnnotationDiv();

function displaySelectors(args) {
  var benign_label = 'ok';
  var benign_div = $('#benign')[0];
  addTitle(benign_div, benign_label);
  var benign_selector = createSelectList('benign_selector', 5,
                  null, parent_div = benign_div);
  var malicious_label = 'alert';
  var malicious_div = $('#malicious')[0];
  addTitle(malicious_div, malicious_label);
  var malicious_selector = createSelectList('malicious_selector', 5,
                  null, parent_div = malicious_div);
  displayLabeledInstances(args);
}

function displayLabeledInstances(args) {
  var query = buildQuery('getLabeledInstances', args);
  d3.json(query, function(error, data) {
      addElementsToSelectList('benign_selector', data['benign']);
      addElementsToSelectList('malicious_selector', data['malicious']);
  });
  var fp_selector = $('#benign_selector')[0];
  fp_selector.addEventListener('change', function() {
      selected_instance_id = getSelectedOption(this);
      last_instance_selector = this;
      printInstanceInformation(selected_instance_id, '');
  });
  var fn_selector = $('#malicious_selector')[0];
  fn_selector.addEventListener('change', function() {
      selected_instance_id = getSelectedOption(this);
      last_instance_selector = this;
      printInstanceInformation(selected_instance_id, '');
  });
}
