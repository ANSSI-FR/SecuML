var path = window.location.pathname.split('/');
var exp_id     = path[2];
var iteration   = path[3];

var exp_type        = 'ActiveLearning';
var label_method      = 'annotation';

var current_label        = null;
var families_list        = null;
var num_families         = null;
var current_family_index = null;

var instances_list         = null;
var confidence_list        = null;
var num_instances          = null;
var current_instance_index = null;
var annotation_queries = null;
var conf = null;


function getCurrentInstance() {
  return instances_list[current_instance_index];
}

function callback() {
    conf.interactive = false;
    if (!conf.core_conf.auto) {
        var current_iteration = currentAnnotationIteration(
                                        exp_id);
        conf.interactive = iteration == current_iteration;
    }
    d3.json(buildQuery('getRcdClusteringId', [exp_id, iteration]),
      function(data) {
        var clustering_exp_id = data['clustering_exp_id'];
        var main = $('#main')[0];
        var nav_bars = createDivWithClass('nav_bars', 'col-md-12',
                                          parent_div=main);
        displayAnnotationDivision();
        var annotations_type = 'individual';
        if (clustering_exp_id != -1) {
            annotations_type = 'families';
        }
        displayInstancesToAnnotate(annotations_type, clustering_exp_id);
        addShortcuts();
      }
    );
}

loadConfigurationFile(exp_id, callback);

function displayInstancesToAnnotate(annotations_type, clustering_exp) {
    displayNavbars('primary', annotations_type, clustering_exp);
    if (annotations_type == 'families') {
      var query = buildQuery('getFamiliesInstancesToAnnotate',
                             [exp_id, iteration, 'all']);
      d3.json(query, function(data) {
          annotation_queries = data;
          families_list = Object.keys(data);
          // The families with no annotation query are not displayed.
          families_list = families_list.filter(
                    function nonEmpty(x) {
                        return annotation_queries[x]['instance_ids'].length > 0
                    });
          num_families = families_list.length;
          current_family_index = 0;
          updateFamilyNavbar();
      });
    } else if (annotations_type == 'individual') {
      var query = buildQuery('getInstancesToAnnotate',
                             [exp_id, iteration, label]);
      d3.json(query, function(data) {
          instances_list = data['instances'];
          families_list = null;
          num_families = null;
          current_family_index = null;
          confidence_list = null;
          num_instances = instances_list.length;
          current_instance_index = 0;
          updateInstanceNavbar();
      });
    }
}

function displayFamilyInstancesToAnnotate(family) {
  instances_list  = annotation_queries[family]['instance_ids'];
  confidence_list = annotation_queries[family]['confidence'];
  num_instances = instances_list.length;
  current_instance_index = 0;
  updateInstanceNavbar();
}

function displayNextInstance() {
  if (current_instance_index <= num_instances-2) {
    current_instance_index += 1;
    updateInstanceNavbar();
  } else {
    displayNextFamily();
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
  iter_family.appendChild(document.createTextNode(
                          (current_family_index+1) + ' / ' + num_families));
  var current_family = cleanDiv('current_family');
  var current_family_label = document.createElement('label');
  current_family_label.setAttribute('class', 'label label-primary');
  current_family_label.appendChild(
    document.createTextNode(families_list[current_family_index]));
  current_family.appendChild(current_family_label);
  displayFamilyInstancesToAnnotate(families_list[current_family_index]);
}

function updateInstanceNavbar() {
  var iter_label = cleanDiv('iter_label');
  iter_label.appendChild(document.createTextNode(
                          (current_instance_index+1) + ' / ' + num_instances));
  var suggested_family = null;
  var suggested_label  = null;
  if (confidence_list) {
    if (confidence_list[current_instance_index] == 'high') {
      suggested_family = families_list[current_family_index];
      suggested_label  = annotation_queries[suggested_family]['label'];
    }
  }
  printInstanceInformation(instances_list[current_instance_index],
                           proba=null,
                           suggested_label,
                           suggested_family);
}

function displayNavbars(type, annotations_type, clustering_exp) {
  var nav_bars = cleanDiv('nav_bars');
  var panel_body = createPanel('panel-' + type, 'col-md-10',
          'Annotation Queries',
          nav_bars);
  var col = createDivWithClass(null, 'col-md-10', panel_body);
  if (annotations_type == 'families') {
    displayFamiliesBar(col, type, clustering_exp);
  }
  displayAnnotationQueriesBar(col, type);

  var col = createDivWithClass(null, 'col-md-2', panel_body);
  clusteringVisualization(col, clustering_exp);
  displayEndButton(col);
}

function clusteringVisualization(row, clustering_exp) {
  function displayClustering(clustering_exp) {
    return function() {
      var query = buildQuery('SecuML', [clustering_exp]);
      window.open(query);
    }
  }
  var group = createDivWithClass('', 'row', row);
  var button = document.createElement('button');
  button.setAttribute('class', 'btn btn-default');
  button.setAttribute('type', 'button');
  button.setAttribute('id', 'button_clustering');
  var button_text = document.createTextNode('Display Families');
  button.appendChild(button_text);
  button.addEventListener('click', displayClustering(clustering_exp));
  group.appendChild(button);
}

function displayFamiliesBar(panel_body, type, clustering_exp) {
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
  var prev_next_group = createDivWithClass('', 'form-group ' + col_size, row);
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

function displayEndButton(row) {
  if (conf.interactive) {
    var end_group = document.createElement('h3');
    end_group.setAttribute('class', 'row');
    row.appendChild(end_group);
    var end_button = document.createElement('button');
    end_button.setAttribute('class', 'btn btn-primary');
    end_button.setAttribute('type', 'button');
    end_button.setAttribute('id', 'end_button');
    var end_button_text = document.createTextNode('Next Iteration');
    end_button.appendChild(end_button_text);
    end_button.addEventListener('click', runNextIteration(conf));
    end_group.appendChild(end_button);
  }
}

function displayAnnotationQueriesBar(panel_body, type) {
  var row = createDivWithClass(null,  'row', parent_div = panel_body);
  var annotation_query_label = document.createElement('label');
  annotation_query_label.setAttribute('class', 'col-md-4 control-label');
  annotation_query_label.appendChild(document.createTextNode(
                          'Annotation Query'));
  row.appendChild(annotation_query_label);
  var iter_label = document.createElement('label');
  iter_label.setAttribute('class', 'col-md-2 control-label');
  iter_label.setAttribute('id', 'iter_label');
  row.appendChild(iter_label);
  // Prev / Next buttons
  var prev_next_group = createDivWithClass('', 'form-group col-md-2', row);
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
  displayAnnotationDiv(suggestion = true);
}

function displayNextInstanceToAnnotate() {
    displayNextInstance();
}
