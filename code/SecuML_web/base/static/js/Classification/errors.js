var path = window.location.pathname.split('/');
var experiment_id       = path[2];
var train_test          = path[3];

var label_method = 'confusion_matrix';
var label_iteration = 0;

var current_type           = null;
var instances_list         = null;
var current_instance_index = null;
var has_families           = null;

var errors = {'fp': null,
              'fn': null};
var titles = {'fp': 'False Positives',
              'fn': 'Undetected'};

function getCurrentInstance() {
  return instances_list[current_instance_index];
}

var conf = {};

loadConfigurationFile();

function callback() {
  displayDivisions();
  getMisclassifiedInstances();
}

function loadConfigurationFile() {
    $.getJSON(buildQuery('getConf', [experiment_id]),
            function(data) {
                conf = data;
                setInstancesSettings(train_test, experiment_id, conf.oldest_parent, callback);
            }
           );
}

function getMisclassifiedInstances() {
  var query = buildQuery('supervisedLearningMonitoring',
                         [conf.experiment_id, train_test, 'errors']);
  $.getJSON(query,
            function(data) {
               errors['fp'] = Object.keys(data['FP']);
               errors['fn'] = Object.keys(data['FN']);
               displayErrors('fp')();
             }
            );
}

function displayErrors(type) {
  return function() {
      current_type = type;
      displayNavList(current_type);
      instances_list = errors[type];
      num_instances = instances_list.length;
      current_instance_index = 0;
      updateInstanceNavbar();
  }
}

function updateInstanceNavbar() {
  var iter_label = cleanDiv('iter_label');
  if (num_instances > 0) {
    iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
    printInstanceInformation(instances_list[current_instance_index]);
  } else {
    iter_label.appendChild(document.createTextNode('0 / 0'));
  }
}

function displayDivisions() {
  displayButtons();
  displayInstanceRow();
}

function displayButton(buttons_line, l, type) {
  var label_group = document.createElement('h3');
  label_group.setAttribute('class', 'row');
  buttons_line.appendChild(label_group);
  var label_button = document.createElement('button');
  var button_class = 'btn btn-md btn-' + type;
  label_button.setAttribute('class', button_class);
  label_button.setAttribute('type', 'button');
  label_button.setAttribute('id', l + '_button');
  var label_button_text = document.createTextNode(titles[l]);
  label_button.appendChild(label_button_text);
  label_button.addEventListener('click', displayErrors(l));
  label_group.appendChild(label_button);
}

function displayButtons() {
  var row = $('#nav_list')[0];
  var buttons_div = createDivWithClass(null, 'col-md-2', parent_div = row);
  var buttons_line = createDivWithClass(null, 'btn-group-vertical', parent_div = buttons_div);
  displayButton(buttons_line, 'fp', 'primary');
  createDivWithClass(null, 'col-md-1', parent_div = buttons_div);
  displayButton(buttons_line, 'fn', 'primary');
}

function displayNavList(type) {
  var row = $('#nav_list')[0];
  var list = createDivWithClass('list', 'col-md-8', parent_div = row);
  var display_type = 'primary';
  var row = cleanDiv('list');
  var panel_body = createPanel('panel-' + display_type, 'row',
          titles[type], row, false);
  var annotation_query_label = document.createElement('label');
  annotation_query_label.setAttribute('class', 'col-md-2 control-label');
  annotation_query_label.appendChild(document.createTextNode('Error'));
  panel_body.appendChild(annotation_query_label);
  var iter_label = document.createElement('label');
  iter_label.setAttribute('class', 'col-md-2 control-label');
  iter_label.setAttribute('id', 'iter_label');
  panel_body.appendChild(iter_label);
  // Prev / Next buttons
  var prev_next_group = createDivWithClass(null, 'col-md-3', panel_body);
  // Prev button
  var prev_button = document.createElement('button');
  prev_button.setAttribute('class', 'btn btn-' + display_type);
  prev_button.setAttribute('type', 'button');
  prev_button.setAttribute('id', 'prev_button');
  var prev_button_text = document.createTextNode('Prev');
  prev_button.appendChild(prev_button_text);
  prev_button.addEventListener('click', displayPrevInstance);
  prev_next_group.appendChild(prev_button);
  // Next button
  var next_button = document.createElement('button');
  next_button.setAttribute('class', 'btn btn-' + display_type);
  next_button.setAttribute('type', 'button');
  next_button.setAttribute('id', 'next_button');
  var next_button_text = document.createTextNode('Next');
  next_button.appendChild(next_button_text);
  next_button.addEventListener('click', displayNextInstance);
  prev_next_group.appendChild(next_button);
}

function displayInstanceRow() {
  var row = $('#instance')[0];
  var annotation = true;
  displayInstancePanel(row, annotation = annotation);
  displayInstanceInformationStructure();
  if (annotation) {
    displayAnnotationDiv(false, false);
  }
}

function displayNextInstance() {
  if (current_instance_index <= num_instances-2) {
    current_instance_index += 1;
    updateInstanceNavbar();
  }
}

function displayPrevInstance() {
  if (current_instance_index > 0) {
    current_instance_index -= 1;
    updateInstanceNavbar();
  }
}
