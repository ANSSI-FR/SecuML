var tooltip = d3.select('body').append('div')
.attr('class', 'tooltip')
.style('opacity', 0);

var project         = window.location.pathname.split('/')[2];
var dataset         = window.location.pathname.split('/')[3];
var experiment_id   = window.location.pathname.split('/')[4];

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
var last_family = {'malicious': 'other', 'benign': 'other'};

function getCurrentInstance() {
  return getSelectedOption(last_instance_selector);
}

var num_components_to_display = null;
var conf = {}
function loadConfigurationFile(callback) {
  num_components_to_display = getNumComponents();
  d3.json(buildQuery('getConf', args), function(error, data) {
    conf = data;
    conf.projection_type = conf.conf.__type__.split('Configuration')[0];
    callback();
  });
}
loadConfigurationFile(onceConfigurationIsLoaded);

function getNumComponents() {
    var query = buildQuery('getNumComponents',
                    [project, dataset, experiment_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var num_components = xmlHttp.responseText;
    return num_components;
}

function onceConfigurationIsLoaded() {
  generateDivisions(conf);
  displaySettings(conf);
  createInstancesSelectors();
  displayInstanceInformationStructure();
  displayAnnotationDiv();
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
          ['explained_variance', 'cumuled_explained_variance']);
}

function displaySettings(conf) {
  var body = createTable('settings', ['', ''], width = 'width:280px');

  // Project Dataset
  addRow(body, ['Project', project]);
  addRow(body, ['Dataset', dataset]);

  var projection_type = conf.conf['__type__'].split('Configuration')[0];
  addRow(body, ['Projection', projection_type]);
}

function generateDivisions(conf) {
  var main = document.getElementById('main');
  // Experiment
  var row = createDivWithClass(null, 'col-md-12', main);
  var experiment = createExperimentDiv('col-md-3', row);

  //// Visu
  // 1st row: Select components , instances in bin and projected instances
  var row = createDivWithClass(null, 'col-md-12', main);
  //// Select Components
  var col1 = createDivWithClass(null, 'col-md-3', row);
  var select_components = createPanel('panel-primary', null, 'Select the Components', col1);
  select_components.setAttribute('id', 'select_components');
  //// Instances in Bin
  var instances_in_bin = createPanel('panel-primary', null, 'Instances in Bin', col1);
  var col_ok = createDivWithClass(null, 'col-md-6', instances_in_bin);
  var selector_ok = createSelectList('instances_selector_ok', 5, null, col_ok, label = 'Ok');
  var col_ko = createDivWithClass(null, 'col-md-6', instances_in_bin);
  var selector_ko = createSelectList('instances_selector_malicious', 5, null, col_ko, label = 'Malicious');
  //// Projected Data
  var projected_data_graph = createPanel('panel-primary', 'col-md-6', 'Projected Instances',row);
  projected_data_graph.setAttribute('id', 'projected_data_graph');
  var projection_error = createDivWithClass('projection_error', 'col-md-3', row);

  // 2nd row: Selected instance - data and annotation
  var row = createDivWithClass(null, 'col-md-12', main);
  displayInstancePanel(row);
}
