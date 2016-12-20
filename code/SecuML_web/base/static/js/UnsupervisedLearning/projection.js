var tooltip = d3.select('body').append('div')
.attr('class', 'tooltip')
.style('opacity', 0);

var project         = window.location.pathname.split('/')[2];
var dataset         = window.location.pathname.split('/')[3];
var experiment_id   = window.location.pathname.split('/')[4];

var hide_confidential = false;

var experiment_name = getExperimentName(project, dataset, experiment_id);
var experiment_label_id = getExperimentLabelId(
                project, dataset, experiment_id);
var experiment_splitted = experiment_name.split('-')

if (experiment_splitted.length > 1) {
    var label_iteration = experiment_splitted[1];
    var predicted_label = experiment_splitted[2];
    var label_method = 'AL_checking_projection_' + predicted_label;
} else {
    var label_iteration = 0;
    var label_method = 'projection';
}

var inst_dataset = dataset;
var inst_exp_id = experiment_id;
var inst_exp_label_id = experiment_label_id;

var args = [project, dataset, experiment_id];
var last_instance_selector = null;
var last_sublabel = {'malicious': 'other', 'benign': 'other'};

var conf = {}
function loadConfigurationFile(callback) {
  d3.json(buildQuery('getConf', args), function(error, data) {
    conf = data;
    conf.projection_type = conf.conf.__type__.split('Configuration')[0];
    console.log(conf);
    callback();
  });
}
loadConfigurationFile(onceConfigurationIsLoaded);

function onceConfigurationIsLoaded() {
  createInstancesSelectors();
  displayInstanceInformationStructure();
  displayAnnotationDiv();
  var num_components_to_display = conf.conf.num_components;
  if (num_components_to_display > 10) {
      num_components_to_display = 10;
  }
  drawComponentsSelectors(num_components_to_display, printComponents);
  drawComponents(project, dataset, experiment_id, 0, 1);
  if (conf.projection_type == 'Pca') {
    createProjectionErrorDiv();
    drawComponentsErrorEvolution(project, dataset, conf.projection_type, experiment_id);
  }
}

function printComponents(c_x, c_y) {
  return function() {
    drawComponents(project, dataset, experiment_id, 
        c_x.selectedIndex, c_y.selectedIndex); 
  }
}

function createProjectionErrorDiv() {
  column = $('#projection_error')[0];
  var select = document.createElement('SELECT');
  select.setAttribute('id', 'projection_error_select');
  select.setAttribute('size', 1);
  var graph_div = createDiv('projection_error_graph');
  column.appendChild(select);
  column.appendChild(graph_div);
  addElementsToSelectList('projection_error_select',
          ['reconstruction_errors', 'explained_variance', 
          'cumuled_explained_variance']);
}
