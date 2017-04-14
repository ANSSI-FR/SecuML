var project             = window.location.pathname.split('/')[2];
var dataset             = window.location.pathname.split('/')[3];
var experiment_id       = window.location.pathname.split('/')[4];
var experiment_label_id = window.location.pathname.split('/')[5];
var label_iteration     = window.location.pathname.split('/')[6];

var label_method = 'check_label';

var last_family = {'malicious': 'other', 'benign': 'other'};
var last_instance_selector = null;

var inst_dataset      = dataset;
var inst_exp_id       = experiment_id;
var inst_exp_label_id = experiment_label_id;

var instances_list         = null;
var benign_instances       = null;
var malicious_instances    = null;
var current_instance_index = null;

function getCurrentInstance() {
  return instances_list[current_instance_index];
}

var conf = {};
loadConfigurationFile(callback);

function callback() {
  generateDivisions();
  displayInstanceInformationStructure();
  displaySelectors();
  displayAnnotationDiv();
}

function loadConfigurationFile(callback) {
    d3.json(buildQuery('getConf',
                       [project, dataset, experiment_id]),
            function(error, data) {
              conf = data;
              callback();
            }
           );
}

function displaySelectors() {
  var benign_div = $('#benign')[0];
  var benign_selector = createSelectList('benign_selector', 5,
                  null, benign_div, 'Ok');
  var malicious_div = $('#malicious')[0];
  var malicious_selector = createSelectList('malicious_selector', 5,
                  null, malicious_div, 'Alert');
  displayLabeledInstances();
}

function displayLabeledInstances() {
  var query = buildQuery('getLabeledInstances',
                         [project, dataset, experiment_label_id]);
 $.getJSON(query,
           function(data) {
              console.log(data);
              benign_instances = data['benign'];
              console.log(benign_instances);
              malicious_instances = data['malicious'];
              addElementsToSelectList('benign_selector', benign_instances);
              addElementsToSelectList('malicious_selector', malicious_instances);
              var benign_selector = $('#benign_selector')[0];
              var malicious_selector = $('#malicious_selector')[0];
              benign_selector.addEventListener('change', function() {
                  selected_instance_id = getSelectedOption(this);
                  printInstanceInformation(selected_instance_id, data['benign'][selected_instance_id]);
                  instances_list = benign_instances;
                  current_instance_index = benign_selector.selectedIndex;
                  malicious_selector.selectedIndex = -1;
              });
              malicious_selector.addEventListener('change', function() {
                  selected_instance_id = getSelectedOption(this);
                  printInstanceInformation(selected_instance_id, data['malicious'][selected_instance_id]);
                  instances_list = malicious_instances;
                  current_instance_index = malicious_selector.selectedIndex;
                  benign_selector.selectedIndex = -1;
              });
            }
           );
}

function generateDivisions() {
  var main = document.getElementById('main');
  var row = createDivWithClass(null, 'row', main);
  var panel_body = createPanel('panel-primary', 'col-md-4',
          'Annotated Instances',
          row);
  var benign = createDivWithClass('benign', 'col-md-6', panel_body);
  var malicious = createDivWithClass('malicious', 'col-md-6', panel_body);
  var row = createDivWithClass(null, 'row', main);
  displayInstancePanel(row);
}
