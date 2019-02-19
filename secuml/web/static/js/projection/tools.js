function getCurrentInstance() {
  return getSelectedOption(last_instance_selector);
}

function getNumComponents() {
    var query = buildQuery('getNumComponents', [exp_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var num_components = xmlHttp.responseText;
    return num_components;
}

function printComponents(c_x, c_y) {
  return function() {
    drawComponents(exp_id,
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
  addRow(body, ['Project', conf.dataset_conf.project]);
  addRow(body, ['Dataset', conf.dataset_conf.dataset]);

  var projection_type = conf.core_conf['__type__'].split('Conf')[0];
  addRow(body, ['Projection', projection_type]);
}

function generateTitle(conf) {
  var main = $('#row_title')[0];
  var div = createDivWithClass(null, 'page-header', parent_div = main);
  var h1 = document.createElement('h1');
  h1.textContent = 'Projection' + ' - ' + conf.core_conf.algo;
  div.appendChild(h1);
}


function generateDivisions(conf) {
  generateTitle(conf);

  var main = document.getElementById('main');

  //// Visu
  // 1st row: Select components , instances in bin and projected instances
  var row = createDivWithClass(null, 'col-md-12', main);

  var col0 = createDivWithClass(null, 'col-md-3', row);
  var experiment = createExperimentDiv('row', col0);
  var projection_error = createDivWithClass('projection_error', 'row', col0);

  //// Select Components
  var col1 = createDivWithClass(null, 'col-md-3', row);
  var select_components = createPanel('panel-primary', null,
                                      'Select the Components', col1,
                                      'select_components');
  //// Instances in Bin
  var instances_in_bin = createPanel('panel-primary', null, 'Instances in Bin',
                                     col1);
  var col_ok = createDivWithClass(null, 'col-md-6', instances_in_bin);
  var selector_ok = createSelectList('instances_selector_ok', 5, null, col_ok,
                                     label='Ok');
  var col_ko = createDivWithClass(null, 'col-md-6', instances_in_bin);
  var selector_ko = createSelectList('instances_selector_malicious', 5, null,
                                     col_ko, label='Malicious');

  //// Projected Data
  var projected_data_graph = createPanel('panel-primary', 'col-md-6',
                                         'Projected Instances', row,
                                         'projected_data_graph');

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
