var project           = window.location.pathname.split('/')[2];
var dataset           = window.location.pathname.split('/')[3];
var experiment_id     = window.location.pathname.split('/')[4];
var label_iteration   = window.location.pathname.split('/')[5];
var predicted_label   = window.location.pathname.split('/')[6];

var label_method = 'annotation_' + predicted_label;
var experiment_label_id = getExperimentLabelId(
                project, dataset, experiment_id);

var instances_list           = null;
var num_instances            = null;
var current_instance_index   = null;

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

function callback(conf) {
      displayDivisions(conf);
      displayInstancesToAnnotate();
}

function loadConfigurationFile(callback) {
    d3.json(buildQuery('getConf', [project, dataset, experiment_id]),
            function(error, data) {
                conf = data;
                conf.interactive = false;
                if (!conf.conf.auto) {
                    var current_iteration = currentAnnotationIteration(project, dataset,
                            experiment_id);
                    conf.interactive = label_iteration == current_iteration;
                }
                callback(conf);
            }
           );
}

function displayInstancesToAnnotate() {
  var query = buildQuery('getInstancesToAnnotate',
                         [project, dataset, experiment_id, label_iteration, predicted_label]);
  d3.json(query, function(error, data) {
      instances_list = data['instances'];
      current_instance_index = 0;
      num_instances = instances_list.length;
      var iter_label = cleanDiv('iter_label');
      iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
      printInstanceInformation(instances_list[current_instance_index]);
  });
}

function displayNextInstance() {
  if (current_instance_index <= num_instances-2) {
    current_instance_index += 1;
    var iter_label = cleanDiv('iter_label');
    iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
    printInstanceInformation(instances_list[current_instance_index]);
  }
}

function displayNextInstanceToAnnotate() {
    displayNextInstance();
}

function displayPrevInstance() {
  if (current_instance_index > 0) {
    current_instance_index -= 1;
    var iter_label = cleanDiv('iter_label');
    iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
    printInstanceInformation(instances_list[current_instance_index]);
  }
}

function displayDivisions(conf) {
  var main = $('#main')[0];

  // Navigation bar
  var row = createDivWithClass(null,  'row', parent_div = main);
  var panel_body = createPanel('panel-primary', 'col-md-12',
                               null, row);
  var annotation_query_label = document.createElement('label');
  annotation_query_label.setAttribute('class', 'col-lg-2 control-label');
  annotation_query_label.appendChild(document.createTextNode('Annotation Query'));
  panel_body.appendChild(annotation_query_label);
  var iter_label = document.createElement('label');
  iter_label.setAttribute('class', 'col-lg-1 control-label');
  iter_label.setAttribute('id', 'iter_label');
  panel_body.appendChild(iter_label);
  // Prev / Next buttons
  var prev_next_group = createDivWithClass('', 'form-group col-md-3', panel_body);

  var prev_button = document.createElement('button');
  prev_button.setAttribute('class', 'btn btn-primary');
  prev_button.setAttribute('type', 'button');
  prev_button.setAttribute('id', 'prev_button');
  var prev_button_text = document.createTextNode('Prev');
  prev_button.appendChild(prev_button_text);
  prev_button.addEventListener('click', displayPrevInstance);
  prev_next_group.appendChild(prev_button);

  var next_button = document.createElement('button');
  next_button.setAttribute('class', 'btn btn-primary');
  next_button.setAttribute('type', 'button');
  next_button.setAttribute('id', 'next_button');
  var next_button_text = document.createTextNode('Next');
  next_button.appendChild(next_button_text);
  next_button.addEventListener('click', displayNextInstance);
  prev_next_group.appendChild(next_button);

  // End annotation process
  if (conf.interactive) {
    var end_group = createDivWithClass('', 'form-group col-md-3', panel_body);
    var end_button = document.createElement('button');
    end_button.setAttribute('class', 'btn btn-primary');
    end_button.setAttribute('type', 'button');
    end_button.setAttribute('id', 'end_button');
    var end_button_text = document.createTextNode('End');
    end_button.appendChild(end_button_text);
    end_button.addEventListener('click', runNextIteration(conf));
    end_group.appendChild(end_button);
  }

  displayAnnotationDivision(false);
}
