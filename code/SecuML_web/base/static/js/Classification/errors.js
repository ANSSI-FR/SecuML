var project             = window.location.pathname.split('/')[2];
var dataset             = window.location.pathname.split('/')[3];
var experiment_id       = window.location.pathname.split('/')[4];
var train_test          = window.location.pathname.split('/')[5];
var experiment_label_id = window.location.pathname.split('/')[6];

var label_method = 'confusion_matrix';
var label_iteration = 0;

var instances_list = null;
var fp_instances = null;
var fn_instances = null;
var current_instance_index = null;

function getCurrentInstance() {
  return instances_list[current_instance_index];
}

var conf = {};

loadConfigurationFile(function () {
    if (train_test == 'train') {
        inst_dataset = dataset;
        inst_exp_id = experiment_id;
        inst_exp_label_id = experiment_label_id;
        callback();
    } else {
        setInstancesSettings(train_test, project, dataset, experiment_id, experiment_label_id,
            callback);
    }
});

function loadConfigurationFile(callback) {
    $.getJSON(buildQuery('getConf',
                         [project, dataset, experiment_id]),
            function(data) {
                conf = data;
                callback();
            }
           );
}

function callback() {
  displayDivisions();
  displayInstanceInformationStructure();
  displayErrors();
  displayAnnotationDiv();
}

function displayErrors() {
 var query = buildQuery('supervisedLearningMonitoring',
                        [conf.project, conf.dataset, conf.experiment_id, train_test, 'errors']);
 $.getJSON(query,
           function(data) {
              fp_instances = Object.keys(data['FP']);
              fn_instances = Object.keys(data['FN']);
              addElementsToSelectList('fp_selector', fp_instances);
              addElementsToSelectList('fn_selector', fn_instances);
              var fp_selector = $('#fp_selector')[0];
              var fn_selector = $('#fn_selector')[0];
              fp_selector.addEventListener('change', function() {
                  selected_instance_id = getSelectedOption(this);
                  printInstanceInformation(selected_instance_id, data['FP'][selected_instance_id]);
                  instances_list = fp_instances;
                  current_instance_index = fp_selector.selectedIndex;
                  fn_selector.selectedIndex = -1;
              });
              fn_selector.addEventListener('change', function() {
                  selected_instance_id = getSelectedOption(this);
                  printInstanceInformation(selected_instance_id, data['FN'][selected_instance_id]);
                  instances_list = fn_instances;
                  current_instance_index = fn_selector.selectedIndex;
                  fp_selector.selectedIndex = -1;
              });
            }
           );
}

function displayDivisions() {
  // Misclassified instances
  var row1 = $('#row1')[0];
  var errors_panel_body = createPanel('panel-primary', 'col-md-4',
          'Misclassified Instances',
          row1);
  var col_fp = createDivWithClass(null, 'col-md-6',
          parent_div = errors_panel_body);
  var fp_selector = createSelectList('fp_selector', 5, null, col_fp,
          label = 'False Positives');
  var col_fn = createDivWithClass(null, 'col-md-6',
          parent_div = errors_panel_body);
  var fn_selector = createSelectList('fn_selector', 5, null, col_fn,
          label = 'False Negatives');
  // Selected instance - data and annotation
  var row2 = $('#row2')[0];
  displayInstancePanel(row2);
}
