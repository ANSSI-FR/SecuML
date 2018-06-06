var path = window.location.pathname.split('/');
var experiment_id  = path[2];
var train_test     = path[3];
var fold_id        = path[4];
var selected_index = path[5];

var instances_list         = null;
var num_instances          = null;
var current_instance_index = null;
var has_families           = null;

function getCurrentInstance() {
  return instances_list[current_instance_index];
}

var label_method    = 'predictionsAnalysis';
var label_iteration = 'None';

var conf = {};

loadConfigurationFile(function (train_test, experiment_id, conf) {
  setInstancesSettings(train_test, experiment_id, callback);
});

function loadConfigurationFile(callback) {
    $.getJSON(buildQuery('getConf', [experiment_id]),
            function(data) {
              conf = data;
              callback(train_test, experiment_id, conf);
            });
}

function callback() {
  displayDivisions(selected_index);
  displayPredictionsBarplot('barplot_div', conf, train_test, experiment_id,
                            fold_id,
                            barPlotCallback(experiment_id));
  updateInstancesDisplay(experiment_id, selected_index);
}

function updateInstancesDisplay(experiment_id, selected_index) {
  var query = buildQuery('getPredictions',
                         [experiment_id, train_test, fold_id,
                          selected_index]);
  $.getJSON(query,
            function(data) {
                instances_list = data['instances'];
                current_instance_index = 0;
                num_instances = instances_list.length;
                var iter_label = cleanDiv('iter_label');
                if (num_instances > 0) {
                  iter_label.appendChild(
                   document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
                  printInstanceInformation(instances_list[current_instance_index]);
                } else {
                  iter_label.appendChild(document.createTextNode('0 / 0'));
                }
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

function displayNavigationPanel(selected_index) {
  var parent_div = cleanDiv('navigation_row');
  var min_value = +selected_index * 10;
  var max_value = (+selected_index + +1) * 10;
  var panel_body = createPanel('panel-primary', 'col-md-12',
          'Predictions between ' + min_value + '% and ' + max_value + '%',
          parent_div);
  var annotation_query_label = document.createElement('label');
  annotation_query_label.setAttribute('class', 'col-lg-2 control-label');
  annotation_query_label.appendChild(document.createTextNode('Instance'));
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
}

function displayDivisions(selected_index) {
  var main = $('#main')[0];

  // Predictions histogram
  var row = createDivWithClass(null, 'row', main);
  var predictions_panel_body = createCollapsingPanel('panel-primary', 'col-md-4',
                                     'Predictions',
                                     row, null);
  var barplot_div = createDiv('barplot_div',
                  parent_div = predictions_panel_body);

  // Navigation bar
  var row = createDivWithClass(null,  'row', parent_div = main);
  row.setAttribute('id', 'navigation_row');
  displayNavigationPanel(selected_index);

  // Selected instance - data and annotation
  var row = createDivWithClass(null,  'row', parent_div = main);
  displayInstancePanel(row);

  displayInstanceInformationStructure();
  var interactive = !hasGroundTruth(experiment_id);
  displayAnnotationDiv(false, interactive);
}
