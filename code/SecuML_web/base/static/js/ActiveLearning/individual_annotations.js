var project           = window.location.pathname.split('/')[2];
var dataset           = window.location.pathname.split('/')[3];
var experiment_id     = window.location.pathname.split('/')[4];
var label_iteration   = window.location.pathname.split('/')[5];
var predicted_label   = window.location.pathname.split('/')[6];

var hide_confidential = false;

var label_method = 'annotation_' + predicted_label;
var experiment_label_id = getExperimentLabelId(
                project, dataset, experiment_id);

var args = [project, dataset, experiment_id, label_iteration, predicted_label];
var last_instance_selector = null;
var last_sublabel = {'malicious': 'other', 'benign': 'other'};

var inst_dataset = dataset;
var inst_exp_id = experiment_id;
var inst_exp_label_id = experiment_label_id;

displayInstanceInformationStructure();
displayInstancesToAnnotate(args);
displayAnnotationDiv();

function displayInstancesToAnnotate(args) {
  var query = buildQuery('getInstancesToAnnotate', args);
  d3.json(query, function(error, data) {
      addElementsToSelectList('instance_selector', data['instances']);
  });
  var selector = $('#instance_selector')[0];
  selector.addEventListener('change', function() {
      selected_instance_id = getSelectedOption(this);
      printInstanceInformation(selected_instance_id);
  });
  last_instance_selector = selector;
}
