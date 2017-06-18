var path = window.location.pathname.split('/');
var project       = path[2];
var dataset       = path[3];
var experiment_id = path[4];
var analysis      = path[5];

var instances_list           = null;
var num_instances            = null;
var current_instance_index   = null;

function getCurrentInstance() {
  return instances_list[current_instance_index];
}

var label_method    = 'alert';
var label_iteration = 'None';
var experiment_label_id = getExperimentLabelId(
                project, dataset, experiment_id);

var conf = {};

loadConfigurationFile(function () {
  setInstancesSettings('test', project, dataset, experiment_id,
          experiment_label_id, callback);
});

function loadConfigurationFile(callback) {
    $.getJSON(buildQuery('getConf',
                       [project, dataset, experiment_id]),
            function(data) {
              conf = data;
              callback();
            });
}

function callback() {
  displayDivisions();
  displayInstancesToAnnotate(project, dataset, experiment_id, analysis);
}

function displayInstancesToAnnotate(project, dataset, experiment_id, analysis) {
  var query = buildQuery('getAlerts',
                         [project, dataset, experiment_id, analysis]);
  $.getJSON(query,
            function(data) {
                instances_list = data['instances'];
                current_instance_index = 0;
                num_instances = instances_list.length;
                var iter_label = cleanDiv('iter_label');
                iter_label.appendChild(
                 document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
                printInstanceInformation(instances_list[current_instance_index]);
            }
           );
}

function displayNextInstance() {
  if (current_instance_index <= num_instances-2) {
    current_instance_index += 1;
    var iter_label = cleanDiv('iter_label');
    iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
    printInstanceInformation(instances_list[current_instance_index]);
  }
}

function displayPrevInstance() {
  if (current_instance_index > 0) {
    current_instance_index -= 1;
    var iter_label = cleanDiv('iter_label');
    iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
    printInstanceInformation(instances_list[current_instance_index]);
  }
}

function displayDivisions() {
  var main = $('#main')[0];

  // Navigation bar
  var row = createDivWithClass(null,  'row', parent_div = main);
  var panel_body = createPanel('panel-primary', 'col-md-12',
          null,
          row);
  var annotation_query_label = document.createElement('label');
  annotation_query_label.setAttribute('class', 'col-lg-2 control-label');
  annotation_query_label.appendChild(document.createTextNode('Alert'));
  panel_body.appendChild(annotation_query_label);
  var iter_label = document.createElement('label');
  iter_label.setAttribute('class', 'col-lg-1 control-label');
  iter_label.setAttribute('id', 'iter_label');
  panel_body.appendChild(iter_label);
  // Prev / Next buttons
  var prev_next_group = createDivWithClass('', 'form-group row', panel_body);
  var button = document.createElement('button');
  button.setAttribute('class', 'btn btn-primary');
  button.setAttribute('type', 'button');
  var button_text = document.createTextNode('Prev');
  button.appendChild(button_text);
  button.addEventListener('click', displayPrevInstance);
  prev_next_group.appendChild(button);
  var button = document.createElement('button');
  button.setAttribute('class', 'btn btn-primary');
  button.setAttribute('type', 'button');
  var button_text = document.createTextNode('Next');
  button.appendChild(button_text);
  button.addEventListener('click', displayNextInstance);
  prev_next_group.appendChild(button);

  // Selected instance - data and annotation
  var row = createDivWithClass(null,  'row', parent_div = main);
  displayInstancePanel(row);

  displayInstanceInformationStructure();
  var interactive = !hasTrueLabels(project, inst_dataset);
  displayAnnotationDiv(false, interactive);
}
