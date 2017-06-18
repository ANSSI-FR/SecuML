var path = window.location.pathname.split('/');
var project           = path[2];
var dataset           = path[3];
var experiment_id     = path[4];
var label_iteration   = path[5];

var label_method        = null;
var experiment_label_id = getExperimentLabelId(project, dataset, experiment_id);

var current_label        = null;
var families_instances   = null;
var families_list        = null;
var num_families         = null;
var current_family_index = null;

var instances_list         = null;
var num_instances          = null;
var current_instance_index = null;

var inst_dataset = dataset;
var inst_exp_id = experiment_id;
var inst_exp_label_id = experiment_label_id;
var has_families = datasetHasFamilies(project, inst_dataset, inst_exp_label_id);

$(document).keypress(function (e) {
   var key = e.keyCode;
   if(key == 13){
      $('#ok_button').click();
      return false;
   } else if(key == 39){
      $('#next_button').click();
      return false;
   } else if(key == 37){
      $('#prev_button').click();
      return false;
   }
});

var conf = {};
loadConfigurationFile(callback);

function getCurrentInstance() {
  return instances_list[current_instance_index];
}

function callback() {
    displayButtons();
    displayAnnotationDivision();
    displayFamilies('malicious', 'danger')();
}

function loadConfigurationFile(callback) {
    d3.json(buildQuery('getConf', [project, dataset, experiment_id]),
            function(error, data) {
                conf = data;
                callback();
            }
           );
}

function displayFamilies(label, type) {
  return function () {
    current_label = label;
    current_type  = type;
    label_method  = 'annotation_' + label;
    displayNavbars(type);
    displayLabelBarplot(type);
  }
}

function displayFamilyInstances(family) {
  instances_list = families_instances[family];
  num_instances  = instances_list.length;
  current_instance_index = 0;
  updateInstanceNavbar();
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

function displayNextFamily() {
  if (current_family_index <= num_families-2) {
    current_family_index += 1;
    updateFamilyNavbar();
  }
}

function displayPrevFamily() {
  if (current_family_index > 0) {
    current_family_index -= 1;
    updateFamilyNavbar();
  }
}

function updateFamilyNavbar() {
  var iter_family = cleanDiv('iter_family');
  iter_family.appendChild(document.createTextNode((current_family_index+1) + ' / ' + num_families));
  var current_family = cleanDiv('current_family');
  var current_family_label = document.createElement('label');
  current_family_label.setAttribute('class', 'label label-' + current_type);
  current_family_label.appendChild(
    document.createTextNode(families_list[current_family_index]));
  current_family.appendChild(current_family_label);
  displayFamilyInstances(families_list[current_family_index]);
}

function updateInstanceNavbar() {
  var iter_label = cleanDiv('iter_label');
  iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
  printInstanceInformation(instances_list[current_instance_index]);
}

function displayButton(buttons_group, l, type) {
  var label_group = createDivWithClass(null, 'btn-group', parent_div = buttons_group);
  var label_button = document.createElement('button');
  label_button.setAttribute('class', 'btn btn-lg btn-' + type);
  label_button.setAttribute('type', 'button');
  label_button.setAttribute('id', l + '_button');
  var label_button_text = document.createTextNode(upperCaseFirst(l));
  label_button.appendChild(label_button_text);
  label_button.addEventListener('click', displayFamilies(l, type));
  label_group.appendChild(label_button);
}

function displayButtons() {
  var main = $('#main')[0];
  var buttons_group = createDivWithClass(null, 'btn-group btn-group-justified', parent_div = main);
  displayButton(buttons_group, 'malicious', 'danger');
  displayButton(buttons_group, 'benign', 'success');
  var nav_bars = createDivWithClass('nav_bars', 'col-md-12', parent_div = main);
}

function displayNavbars(type) {
  var nav_bars = cleanDiv('nav_bars');
  var panel_body = createPanel('panel-' + type, 'col-md-6',
          'Annotated Instances',
          nav_bars);
  displayFamiliesBar(panel_body, type);
  displayInstancesBar(panel_body, type);
  var query = buildQuery('getFamiliesInstances',
                         [project, dataset, experiment_label_id,
                          current_label, label_iteration-1]);
  d3.json(query, function(error, data) {
      families_instances = data;
      families_list = Object.keys(families_instances);
      num_families = families_list.length;
      current_family_index = 0;
      updateFamilyNavbar();
  });
}

function selectFamilyFromBarPlot(selected_bar) {
    var selected_index = selected_bar[0]._index;
    var selected_family = selected_bar[0]._model.label;
    current_family_index = families_list.indexOf(selected_family)
    updateFamilyNavbar();
}

function displayLabelBarplot(type) {
  var nav_bars = document.getElementById('nav_bars');
  var panel_body = createCollapsingPanel('panel-' + type, 'col-md-6',
          'Families Statistics',
          nav_bars,
          collapse_id = 'barplot');
  var query = buildQuery('getFamiliesBarplot',
                         [project, dataset, experiment_id, label_iteration, current_label]);
  var div = document.getElementById('barplot');
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data, 'Families');
      var barPlot = drawBarPlot('barplot',
                                options, data,
                                type = 'bar', width = null, height = null,
                                callback = selectFamilyFromBarPlot);
      div.style.height = '350px';
  });
}

function displayFamiliesBar(panel_body, type) {
  var col_size = 'col-md-2';
  var row = createDivWithClass(null,  'row', parent_div = panel_body);
  var annotation_query_family = document.createElement('label');
  annotation_query_family.setAttribute('class', col_size + ' control-label');
  var family_label = document.createElement('label');
  family_label.appendChild(document.createTextNode('Family'))
  annotation_query_family.appendChild(family_label);
  //annotation_query_family.appendChild(document.createTextNode('Family'));
  row.appendChild(annotation_query_family);
  var current_family_header = document.createElement('h4');
  row.appendChild(current_family_header);
  var current_family = document.createElement('label');
  current_family.setAttribute('class', col_size + ' control-label');
  current_family.setAttribute('id', 'current_family');
  current_family_header.appendChild(current_family);
  var iter_family = document.createElement('label');
  iter_family.setAttribute('class', col_size + ' control-label');
  iter_family.setAttribute('id', 'iter_family');
  row.appendChild(iter_family);
  // Prev / Next buttons
  var prev_next_group = createDivWithClass('', 'form-group row', row);
  // Prev button
  var prev_button = document.createElement('button');
  prev_button.setAttribute('class', 'btn btn-' + type);
  prev_button.setAttribute('type', 'button');
  prev_button.setAttribute('id', 'prev_button_family');
  var prev_button_text = document.createTextNode('Prev');
  prev_button.appendChild(prev_button_text);
  prev_button.addEventListener('click', displayPrevFamily);
  prev_next_group.appendChild(prev_button);
  // Next button
  var next_button = document.createElement('button');
  next_button.setAttribute('class', 'btn btn-' + type);
  next_button.setAttribute('type', 'button');
  next_button.setAttribute('id', 'next_button_family');
  var next_button_text = document.createTextNode('Next');
  next_button.appendChild(next_button_text);
  next_button.addEventListener('click', displayNextFamily);
  prev_next_group.appendChild(next_button);
}

function displayInstancesBar(panel_body, type) {
  var row = createDivWithClass(null,  'row', parent_div = panel_body);
  var annotation_query_label = document.createElement('label');
  annotation_query_label.setAttribute('class', 'col-md-4 control-label');
  annotation_query_label.appendChild(document.createTextNode('Instance'));
  row.appendChild(annotation_query_label);
  var iter_label = document.createElement('label');
  iter_label.setAttribute('class', 'col-md-2 control-label');
  iter_label.setAttribute('id', 'iter_label');
  row.appendChild(iter_label);
  // Prev / Next buttons
  var prev_next_group = createDivWithClass('', 'form-group row', row);
  // Prev button
  var prev_button = document.createElement('button');
  prev_button.setAttribute('class', 'btn btn-' + type);
  prev_button.setAttribute('type', 'button');
  prev_button.setAttribute('id', 'prev_button');
  var prev_button_text = document.createTextNode('Prev');
  prev_button.appendChild(prev_button_text);
  prev_button.addEventListener('click', displayPrevInstance);
  prev_next_group.appendChild(prev_button);
  // Next button
  var next_button = document.createElement('button');
  next_button.setAttribute('class', 'btn btn-' + type);
  next_button.setAttribute('type', 'button');
  next_button.setAttribute('id', 'next_button');
  var next_button_text = document.createTextNode('Next');
  next_button.appendChild(next_button_text);
  next_button.addEventListener('click', displayNextInstance);
  prev_next_group.appendChild(next_button);
}

function displayAnnotationDivision() {
  var main = $('#main')[0];
  // Selected instance - data and annotation
  var row = createDivWithClass(null,  'row', parent_div = main);
  displayInstancePanel(row);
  displayInstanceInformationStructure();
  displayAnnotationDiv(suggestion = false);
}
