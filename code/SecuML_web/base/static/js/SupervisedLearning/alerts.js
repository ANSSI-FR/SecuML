var project       = window.location.pathname.split('/')[2];
var dataset       = window.location.pathname.split('/')[3];
var experiment_id = window.location.pathname.split('/')[4];
var iteration     = window.location.pathname.split('/')[5];
var analysis      = window.location.pathname.split('/')[6];

var hide_confidential = false;

var label_method    = 'alert';
var label_iteration = iteration;
var experiment_label_id = getExperimentLabelId(
                project, dataset, experiment_id);

var args = [project, dataset, experiment_id, label_iteration, analysis];
var last_instance_selector = null;
var last_sublabel = {'malicious': 'other', 'benign': 'other'};
var last_instance_selector = null;

setInstancesSettings('alerts', project, dataset, experiment_id, experiment_label_id,
        callback);

function callback() {
  displayInstanceInformationStructure();
  displayInstancesToAnnotate(args);
  displayAnnotationDiv();
}

function displayInstancesToAnnotate(args) {
  var query = buildQuery('getAlerts', args);
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
