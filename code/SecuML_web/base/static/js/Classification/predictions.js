var path = window.location.pathname.split('/');
var project        = path[2];
var dataset        = path[3];
var experiment_id  = path[4];
var train_test     = path[5];
var selected_index = path[6];

var instances_list           = null;
var num_instances            = null;
var current_instance_index   = null;
var has_families             = null;

function getCurrentInstance() {
  return instances_list[current_instance_index];
}

var label_method    = 'predictionsAnalysis';
var label_iteration = 'None';
var experiment_label_id = getExperimentLabelId(
                project, dataset, experiment_id);

var conf = {};

loadConfigurationFile(function () {
  setInstancesSettings(train_test, project, dataset, experiment_id,
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
  displayDivisions(selected_index);
  displayPredictionBarplot();
  updateInstancesDisplay(project, dataset, experiment_id, selected_index);
}

function updateInstancesDisplay(project, dataset, experiment_id, selected_index) {
  var query = buildQuery('getPredictions',
                         [project, dataset, experiment_id, train_test, selected_index]);
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

function updateDisplay(selected_bar) {
    var selected_index = selected_bar[0]._index;
    displayNavigationPanel(selected_index);
    updateInstancesDisplay(project, dataset, experiment_id, selected_index);
}

function displayPredictionBarplot() {
    var div_obj = cleanDiv('barplot_div');
    var exp_type = conf.__type__.split('Experiment')[0];
    if (validationWithoutTrueLabels(train_test, conf, exp_type)) {
      var get_function = 'predictions_barplot';
    } else {
      var get_function = 'predictions_barplot_labels';
    }
    var query = buildQuery('supervisedLearningMonitoring',
                           [conf.project, conf.dataset, experiment_id, train_test, get_function]);
    $.getJSON(query, function (data) {
        var options = barPlotOptions(data);
        var barPlot = drawBarPlot(div_obj.id,
                                  options,
                                  data,
                                  type = 'bar',
                                  width = null,
                                  height = null,
                                  callback = updateDisplay);
        div_obj.style.height = '400px';
    });
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
  var interactive = !hasTrueLabels(project, inst_dataset);
  displayAnnotationDiv(false, interactive);
}
