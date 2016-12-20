var project         = window.location.pathname.split('/')[2];
var dataset         = window.location.pathname.split('/')[3];
var experiment_id   = window.location.pathname.split('/')[4];

var hide_confidential = false;
var quick_clustering  = true;

var experiment_label_id = getExperimentLabelId(
                project, dataset, experiment_id);
var experiment_name     = getExperimentName(project, dataset, experiment_id);
var experiment_splitted = experiment_name.split('-')
len = experiment_splitted.length
if (len > 1) {
    var label_iteration = experiment_splitted[len-2];
    var predicted_label = experiment_splitted[len-1];
    var label_method = 'AL_checking_clustering_' + predicted_label;
} else {
    var label_iteration = 0;
    var label_method = 'clustering';
}

var inst_dataset = dataset;
var inst_exp_id = experiment_id;
var inst_exp_label_id = experiment_label_id;

var args = [project, dataset, experiment_id];

var last_instance_selector = null;
var last_sublabel = {'malicious': 'other', 'benign': 'other'};

function loadConfigurationFile(project, dataset, experiment_id, callback) {
  d3.json(buildQuery('getConf', args), function(error, data) {
    conf = data;
    callback();
  });
}

var conf = {}
loadConfigurationFile(project, dataset, experiment_id,
        onceConfigurationIsLoaded);

function displayClusterIdSelection() {
    var cluster_id_div = cleanDiv('cluster_id');
    var select = createSelectList('select_cluster_id',
            5, displayCluster, parent_div = cluster_id_div);
    //var get_colors  = '/getClustersColors/' + conf.num_clusters + '/';
    var get_labels  = buildQuery('getClustersLabels', [project, dataset, experiment_id]);
    //d3.json(get_colors, function(error, data) {
    d3.json(get_labels, function(error, data) {
        //var colors = data.colors;
        var labels = data.labels;
        // Display the selector for the cluster index
        for (var c = 0; c < conf.conf.num_clusters; c++) {
                var opt = document.createElement('option');
                //if (labels[c].indexOf('unknown_') == 0) {
                //  opt.text = labels[c];
                //} else {
                //  opt.text = labels[c].split('__')[1];
                //}
                opt.text = 'c_' + c;
                opt.value = c;
                //opt.style.background = colors[c];
                select_cluster_id.add(opt);
        }
    });
}

function onceConfigurationIsLoaded() {
  generateClusteringDivisions();
  displayInstanceInformationStructure();
  cleanCluster();
  displayClusterIdSelection();
  displayClustersStats();
  displayAnnotationDiv();
  clusterLabel();
}

function displayClustersStats() {
  var experiment_label_id_tmp = experiment_label_id;
  var num_instances_per_cluster_file = buildQuery('getClusterStats',
          [project, dataset, experiment_id]);
  drawBarPlotFromPath('clusters_labels_stats', num_instances_per_cluster_file,
          'cluster', 'num instances', false, displayClusterInstances);
}

function displayCluster() {
  var selected_cluster = getSelectedOption(select_cluster_id);
  cleanCluster();
  updateLastSublabel(project, dataset, experiment_id, selected_cluster);
  displayNumElementsDistortion(project, dataset, experiment_id, selected_cluster);
  displayClusterInstances();
}

function updateLastSublabel(project, dataset, experiment_id, selected_cluster) {
  var query = buildQuery('getClusterLabel',
          [project, dataset, experiment_id, selected_cluster]);
  $.get(query, function(data, status) {
      if (data != 'None') {
        var label = data.split('__')[0];
        var sublabel = data.split('__')[1]
        last_sublabel[label] = sublabel;
      }
  });
}

function displayClusterInstances() {
  var selected_cluster = getSelectedOption(select_cluster_id);
  var radio_position = $('#radio_position')[0];
  var radio_label = $('#radio_label')[0];
  if (radio_position.checked) {
    displayClusterInstancesByPosition();
  } else if (radio_label.checked) {
    displayClusterInstancesBySublabel(selected_cluster);
  }
}

function cleanCluster() {
  cleanDiv('instances_in_cluster');
  cleanInstanceInformation();
}

function displayClusterInstancesBySublabel(selected_cluster) {
  createPerLabelSelectors('Sublabels');
  var label_selector = $('#select_labels')[0];
  var instance_selector = $('#select_instances_label_sublabel')[0];
  var query = buildQuery('getClusterLabelsSublabels',
          args.concat([selected_cluster]));
  d3.json(query, function(error, data) {
      labels_sublabels = [];
      labels = Object.keys(data);
      for (l in labels) {
        label = labels[l];
        sublabels = Object.keys(data[label]);
        for (q in sublabels) {
          sublabel = sublabels[q];
          labels_sublabels.push(label + '-' + sublabel);
        }
      }
      addElementsToSelectList('select_labels', labels_sublabels);
  });
  label_selector.addEventListener('change', function() {
      cleanDiv('select_instances_label_sublabel');
      selected_label_sublabel = getSelectedOption(label_selector);
      selected_label = selected_label_sublabel.split('-')[0];
      selected_sublabel = selected_label_sublabel.split('-')[1];
      var query = buildQuery('getClusterLabelSublabelIds',
          args.concat(selected_cluster, selected_label,
                  selected_sublabel, conf.conf.num_results));
      d3.json(query, function(error, data) {
          ids = data.ids;
          addElementsToSelectList(
                          'select_instances_label_sublabel', ids);
      });
  });
}

function displayClusterInstancesByPosition() {
    var instances_div = cleanDiv('instances_in_cluster');
    var position_label = createDivWithClass('position_label_div', 'row',
            parent_div = instances_div);
    var titles = ['Center', 'Edge', 'Random'];
    var selects = ['center', 'edge', 'random'];
    for (var i = 0; i < titles.length; i++) {
      var pos = selects[i];
      var select_position_div = createDivWithClass('None', 'col-md-4',
              parent_div = instances_div, title = titles[i]);
      var select = createSelectList('select_' + pos + '_instances',
                      5,
                      function() {
                        selected_instance_id = getSelectedOption(this);
                        printInstanceInformation(selected_instance_id, '');
                        last_instance_selector = this;
                      },
                      select_position_div);
      var selected_cluster = getSelectedOption(select_cluster_id);
      displayInstancesInOneSelector(selected_cluster, pos[0]);
    }
}

function displayNumElementsDistortion(project, dataset, experiment, selected_cluster) {
    var query = buildQuery('getNumElementsDistortion', [project, dataset, experiment_id, selected_cluster]);
    d3.json(query, function(error, data) {
        var num_elements = data.num_elements;
        $('#cluster_info_id')[0].firstChild.nodeValue = 'c_' + selected_cluster;
        var elements = ' element';
        if (num_elements > 1) {
            elements += 's';
        }
        $('#cluster_info_num_elements')[0].firstChild.nodeValue = num_elements + elements;
    });
}

function displayInstancesInOneSelector(selected_cluster, c_e_r) {
  // Get the ids belonging to the selected cluster
  var instance_selector = null;
  if (c_e_r == 'c') {
      instance_selector = 'select_center_instances';
  } else if (c_e_r == 'e') {
      instance_selector = 'select_edge_instances';
  } else if (c_e_r == 'r') {
      instance_selector = 'select_random_instances';
  }
  var query = buildQuery('getClusterInstances', 
          [project, dataset, experiment_id, selected_cluster, c_e_r, conf.conf.num_results]);
  d3.json(query, function(error, data) {
    ids = data[selected_cluster];
    addElementsToSelectList(instance_selector, ids);
  });
}

/////////////////////////////////////////
/////////////////////////////////////////
// Cluster labeling
/////////////////////////////////////////
/////////////////////////////////////////

function clusterLabel() {
  var label_div = $('#cluster_labels')[0];
  // Remove button
  var remove_row = createDivWithClass('None', 'row',
          parent_div = label_div);
  var button_remove = document.createElement('button');
  button_remove.appendChild(document.createTextNode('Remove'));
  button_remove.addEventListener('click', function() {
      var selected_cluster = getSelectedOption(select_cluster_id);
      var query = buildQuery('removeClusterLabel', args.concat(
              [selected_cluster, conf.conf.num_results]));
      $.ajax({url: query});
      displayClustersStats();
  });
  remove_row.appendChild(button_remove);
  var label_row = createDivWithClass('None', 'row',
          parent_div = label_div);
  var malicious_col = displaySublabelSelector(label_row, 'malicious', cluster = true);
  var benign_col    = displaySublabelSelector(label_row, 'benign', cluster = true);
  // Add button
  // Malicious
  var malicious_label = 'alert';
  var malicious_button = document.createElement('button');
  var malicious_text = document.createTextNode(malicious_label);
  malicious_button.appendChild(malicious_text);
  malicious_button.addEventListener('click', function() {
      var selected_cluster = getSelectedOption(select_cluster_id);
      var sublabel = $('#' + 'cluster_' + 'malicious' + '_sublabel_selector').val();
      if (!sublabel) {
          alert('A sublabel must be selected.');
          return;
      }
      var query = buildQuery('addClusterLabel', args.concat(
              [selected_cluster, conf.conf.num_results,
              'malicious', sublabel,
              label_iteration, label_method]));
      $.ajax({url: query});
      displayClustersStats();
  });
  malicious_col.appendChild(malicious_button);
  // Benign
  var benign_label = 'ok';
  var benign_button =  document.createElement('button');
  var benign_text = document.createTextNode(benign_label);
  benign_button.appendChild(benign_text);
  benign_button.addEventListener('click', function() {
      var selected_cluster = getSelectedOption(select_cluster_id);
      var sublabel = $('#' + 'cluster_' + 'benign' + '_sublabel_selector').val();
      if (!sublabel) {
          alert('A sublabel must be selected.');
          return;
      }
      var query = buildQuery('addClusterLabel', args.concat(
              [selected_cluster, conf.conf.num_results,
              'benign', sublabel,
              label_iteration,
              label_method]));
      $.ajax({url: query});
      displayCluster(selected_cluster);
      displayClustersStats();
  });
  benign_col.appendChild(benign_button);
}

/////////////////////////////////////////
/////////////////////////////////////////
// Pages elements
/////////////////////////////////////////
/////////////////////////////////////////

function generateClusteringDivisions() {

  var first_col = $('#first_col')[0];

  /////// First row
  var row = createDivWithClass('first_row',
          'row', parent_div = first_col);
  var selectors_column = createDivWithClass('None',
                  'col-md-4', parent_div = row);
  var cluster_id_column = createDivWithClass('None', 'row',
          parent_div = selectors_column, title = 'Clusters');
  var cluster_id = createDiv('cluster_id',
          parent_div = cluster_id_column);
  // Clusters Labels
  var num_instances_column = createDivWithClass(
                  'None', 'col-md-8',
                  parent_div = row,
                  title = 'Clusters Labels');
  var labels_true_labels = createDivWithClass('labels_true_labels_div', 'row',
                  parent_div = num_instances_column);
  var clusters_labels_stats = createDiv('clusters_labels_stats',
                  parent_div = num_instances_column);
  ///// Second row
  var row = createDivWithClass('second_row',
          'row', parent_div = first_col);
  var first_col = createDivWithClass('None',
          'col-md-6', parent_div = row);
  var selected_cluster_row = createDivWithClass('None', 'row',
          parent_div = first_col,
          title = 'Selected Cluster');
  var selected_cluster_info = createDiv('selected_cluster_info',
          parent_div = selected_cluster_row);
  var ul = document.createElement('ul');
  var li_cluster_id = document.createElement('li');
  li_cluster_id.setAttribute('id', 'cluster_info_id');
  li_cluster_id.appendChild(document.createTextNode('None'));
  ul.appendChild(li_cluster_id);
  var li_num_elements = document.createElement('li');
  li_num_elements.appendChild(document.createTextNode('None'));
  li_num_elements.setAttribute('id', 'cluster_info_num_elements');
  ul.appendChild(li_num_elements);
  selected_cluster_info.appendChild(ul);

  var cluster_labels_row = createDivWithClass('None', 'row',
          parent_div = first_col, title = 'Annotate the Whole Cluster');
  cluster_labels = createDiv('cluster_labels',
          parent_div = cluster_labels_row);
  var second_col = createDivWithClass('None',
          'col-md-6', parent_div = row);
  var position_label = createDivWithClass('position_label_div', 'row',
          parent_div = second_col);
  var radio_position = makeRadioButton('radio_cluster_instances',
    'position', 'Position', true, displayClusterInstances,
    parent_div = position_label);
  var radio_label = makeRadioButton('radio_cluster_instances',
    'label', 'Label', false, displayClusterInstances,
    parent_div = position_label);
  // Instances in cluster
  var instances_in_cluster = createDivWithClass('instances_in_cluster', 'row',
          parent_div = second_col);

  ///// Second column - instance information
  var second_col = $('#second_col')[0];
  var row = createDivWithClass('None', 'row',
          parent_div = second_col);
  var ident_col = createDivWithClass('None', 'col-md-4',
          parent_div = row, title = 'Instance');
  var ident_div = createDiv('instance_ident',
          parent_div= ident_col);
  var label_col = createDivWithClass('None', 'col-md-8',
          parent_div = row);
  var label_div = createDiv('instance_label',
          parent_div = label_col);
  var second_row = createDivWithClass('None', 'row',
          parent_div = second_col);
  var instance_data = createDiv('instance_data',
          parent_div = second_row);
}

function createPerLabelSelectors(labels_sublabels) {
  var instances_div = cleanDiv('instances_in_cluster');
  var labels_column = createDivWithClass('None', 'col-md-6',
                  parent_div = instances_div,
                  title = labels_sublabels);
  var select_labels = createSelectList('select_labels',
                  5, null, labels_column);
  var instances_column = createDivWithClass('None',
                  'col-md-6',
                  parent_div = instances_div,
                  title = 'Instances');
  var select_instances = createSelectList(
                  'select_instances_label_sublabel',
                  5,
                  function() {
                    selected_instance_id = getSelectedOption(this);
                    printInstanceInformation(selected_instance_id, '');
                  },
                  parent_div = instances_column);
}
