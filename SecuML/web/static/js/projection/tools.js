function getCurrentInstance() {
  return getSelectedOption(last_instance_selector);
}

function loadConfigurationFile(callback) {
  num_components_to_display = getNumComponents();
  d3.json(buildQuery('getConf', [experiment_id]), function(error, data) {
    conf = data;
    conf.projection_type = conf.core_conf.__type__.split('Conf')[0];
    setInstancesSettings('train', experiment_id);
    callback();
  });
}

function getNumComponents() {
    var query = buildQuery('getNumComponents', [experiment_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var num_components = xmlHttp.responseText;
    return num_components;
}

function onceConfigurationIsLoaded(type) {
  return function() {
    generateDivisions(conf, type);
    displaySettings(conf, type);
    createInstancesSelectors();
    displayInstanceInformationStructure();
    displayAnnotationDiv();
    if (num_components_to_display > 10) {
        num_components_to_display = 10;
    }
    drawComponentsSelectors(num_components_to_display, printComponents);
    drawComponents(experiment_id, 0, 1);
    if (conf.projection_type == 'Pca') {
      createProjectionErrorDiv();
      drawComponentsErrorEvolution(conf.projection_type, experiment_id);
    }
  }
}

function printComponents(c_x, c_y) {
  return function() {
    drawComponents(experiment_id,
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

function displaySettings(conf, type) {
  var body = createTable('settings', ['', ''], width = 'width:280px');

  // Project Dataset
  addRow(body, ['Project', conf.dataset_conf.project]);
  addRow(body, ['Dataset', conf.dataset_conf.dataset]);

  var projection_type = conf.core_conf['__type__'].split('Conf')[0];
  addRow(body, [upperCaseFirst(type), projection_type]);
}

function generateTitle(conf, type) {
  var main = $('#row_title')[0];
  var div = createDivWithClass(null, 'page-header', parent_div = main);
  var h1 = document.createElement('h1');
  h1.textContent = upperCaseFirst(type) + ' - ' + conf.core_conf.algo;
  div.appendChild(h1);
}


function generateDivisions(conf, type) {
  generateTitle(conf, type);

  var main = document.getElementById('main');

  //// Visu
  // 1st row: Select components , instances in bin and projected instances
  var row = createDivWithClass(null, 'col-md-12', main);

  var col0 = createDivWithClass(null, 'col-md-3', row);
  var experiment = createExperimentDiv('row', col0);
  var projection_error = createDivWithClass('projection_error', 'row', col0);

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

  // 2nd row: Selected instance - data and annotation
  var row = createDivWithClass(null, 'col-md-12', main);
  displayInstancePanel(row);
}

function addShortcuts(){
  $(document).keypress(function (e) {
     var key = e.keyCode;
     if(key == 13){
        $('#ok_button').click();
        return false;
     }
  });
}
