var path = window.location.pathname.split('/');
var experiment_id = path[2];

var label_iteration = 0;
var label_method = 'clustering';

var has_families = datasetHasFamilies(experiment_id);

var inst_exp_id = experiment_id;
var inst_exp_label_id = null;

var last_instance_selector = null;
var current_cluster_label  = null;
var current_cluster_family = null;

var clusters_labels = null;

function getCurrentInstance() {
  return getSelectedOption(last_instance_selector);
}

function loadConfigurationFile(experiment_id, callback) {
  $.getJSON(buildQuery('getConf', [experiment_id]),
            function(data) {
              conf = data;
              inst_exp_label_id = conf.oldest_parent;
              callback(conf);
            }
           );
}

var conf = {}
loadConfigurationFile(experiment_id, onceConfigurationIsLoaded);

function displayClusterIdSelection() {
    var callback = function() {
      var selected_cluster = getSelectedOption(select_cluster_id);
      displayCluster(selected_cluster);
    }
    var cluster_id_div = cleanDiv('cluster_id');
    var select = createSelectList('select_cluster_id',
            5, callback, parent_div = cluster_id_div);
    var get_labels  = buildQuery('getClustersLabels', [experiment_id]);
    $.getJSON(get_labels,
              function(data) {
                  clusters_labels = data.clusters;
                  // Display the selector for the cluster index
                  for (var c = 0; c < clusters_labels.length; c++) {
                          var opt = document.createElement('option');
                          opt.text = clusters_labels[c].label;
                          opt.value = clusters_labels[c].id;
                          select_cluster_id.add(opt);
                  }
                  // Display the first cluster
                  select.selectedIndex = 0;
                  displayCluster(0);
              }
             );
}

function onceConfigurationIsLoaded(conf) {
  generateClusteringDivisions();
  displayClusterIdSelection();
  displayClustersStats(conf);
}

function displayClustersStats(conf) {
  var callback = function(active_bars) {
    var selected_index = active_bars[0]._index;
    var selected_cluster = active_bars[0]._view.label.split('_')[1];
    document.getElementById('select_cluster_id').selectedIndex = selected_index;
    var selected_cluster = getSelectedOption(select_cluster_id);
    displayCluster(selected_cluster);
  }
  var query = buildQuery('getClusterStats', [experiment_id]);
  var clusters_stats = $('#clusters_labels_stats')[0];
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data);
      options.responsive = false;
      var bar_plot = drawBarPlot('clusters_labels_stats',
                                 options, data,
                                 type = 'bar',
                                 width = '550',
                                 height = '250',
                                 callback = callback);
  });
}

function displayCluster(selected_cluster) {
  cleanCluster();
  displayNumElements(experiment_id, selected_cluster);
  displayClusterInstances(selected_cluster);
}

function displayClusterInstances(selected_cluster) {
  displayClusterInstancesByPosition(selected_cluster);
  displayClusterInstancesByFamily(selected_cluster);
}

function cleanCluster() {
  cleanDiv('instances_by_label');
  cleanDiv('instances_by_position');
  //displayAnnotationDiv();
  //cleanInstanceInformation();
}

function displayClusterInstancesByFamily(selected_cluster) {
  createPerLabelSelectors('Families');
  var label_selector = $('#select_labels')[0];
  var instance_selector = $('#select_instances_label_family')[0];
  var query = buildQuery('getClusterLabelsFamilies',
                         [experiment_id, selected_cluster]);
  $.getJSON(query,
            function(data) {
                labels_families = [];
                labels = Object.keys(data);
                for (l in labels) {
                  label = labels[l];
                  families = Object.keys(data[label]);
                  for (q in families) {
                    family = families[q];
                    labels_families.push(label + '-' + family);
                  }
                }
                addElementsToSelectList('select_labels', labels_families);
            }
           );
  label_selector.addEventListener('change', function() {
      cleanDiv('select_instances_label_family');
      selected_label_family = getSelectedOption(label_selector);
      var split = selected_label_family.split('-')
      var selected_label = split[0];
      var selected_family = split.slice(1, split.length).join('-');
      var query = buildQuery('getClusterLabelFamilyIds',
                             [experiment_id,
                              selected_cluster, selected_label,
                              selected_family, conf.conf.num_results]);
      $.getJSON(query,
                function(data) {
                    addElementsToSelectList('select_instances_label_family',
                                            data.ids);
                }
               );
  });
}

function displayClusterInstancesByPosition(selected_cluster) {
    var instances_div = cleanDiv('instances_by_position');
    var position_label = createDivWithClass('position_label_div', 'row',
            parent_div = instances_div);
    var titles = ['Center', 'Edge', 'Random'];
    var selects = ['center', 'edge', 'random'];
    for (var i = 0; i < titles.length; i++) {
      var pos = selects[i];
      var select_position_div = createDivWithClass('None', 'col-md-4',
              parent_div = instances_div);
      var select = createSelectList('select_' + pos + '_instances',
                      5,
                      function () {
                          selected_instance_id = getSelectedOption(this);
                          printInstanceInformation(selected_instance_id, '');
                          last_instance_selector = this;
                          // unselect other position selectors
                          for (var j = 0; j < titles.length; j++) {
                            var p = selects[j];
                            var s = document.getElementById('select_' + p + '_instances');
                            if (s != this) {
                              s.selectedIndex = -1;
                            }
                          }
                      },
                      select_position_div,
                      titles[i]);
      displayInstancesInOneSelector(selected_cluster, pos);
    }
}

function displayNumElements(experiment, selected_cluster) {
    var query = buildQuery('getNumElements', [experiment_id, selected_cluster]);
    $.getJSON(query,
              function(data) {
                var num_elements = data.num_elements;
                $('#cluster_info_id')[0].firstChild.nodeValue = clusters_labels[selected_cluster].label;
                //$('#cluster_info_id')[0].firstChild.nodeValue = 'c_' + selected_cluster;
                var elements = ' element';
                if (num_elements > 1) {
                    elements += 's';
                }
                $('#cluster_info_num_elements')[0].firstChild.nodeValue = num_elements + elements;
              }
             );
}

function displayInstancesInOneSelector(selected_cluster, c_e_r) {
  // Get the ids belonging to the selected cluster
  var instance_selector = null;
  if (c_e_r == 'center') {
      instance_selector = 'select_center_instances';
  } else if (c_e_r == 'edge') {
      instance_selector = 'select_edge_instances';
  } else if (c_e_r == 'random') {
      instance_selector = 'select_random_instances';
  }
  var query = buildQuery('getClusterInstancesVisu',
          [experiment_id, selected_cluster, c_e_r[0], conf.conf.num_results]);
  $.getJSON(query,
            function(data) {
              ids = data[selected_cluster];
              addElementsToSelectList(instance_selector, ids);
              if (c_e_r == 'center') {
                  // Display the first instance
                  if (ids.length > 0) {
                    instance_selector.selectedIndex = 0;
                    printInstanceInformation(ids[0], '');
                    last_instance_selector = instance_selector;
                  }
              }
            }
           );
}

/////////////////////////////////////////
/////////////////////////////////////////
// Pages elements
/////////////////////////////////////////
/////////////////////////////////////////

function generateClusteringDivisions() {
  var main = $('#main')[0];

  // First row
  var row = createDivWithClass(null, 'row', main);
  var num_instances_panel_body = createCollapsingPanel('panel-primary', 'col-md-6',
                                     'Clusters Statistics',
                                     row, null);
  var clusters_labels_stats = createDiv('clusters_labels_stats',
                  parent_div = num_instances_panel_body);

  // Second row
  var row = createDivWithClass(null, 'row', main);

  var cluster_selector_panel_body = createPanel('panel-primary', 'col-md-3',
                                     'Select a Cluster',
                                     row);
  var cluster_id_column = createDivWithClass(null, 'row',
          parent_div = cluster_selector_panel_body);
  cluster_id_column = createDivWithClass(null, 'col-md-10',
          parent_div = cluster_id_column);
  var cluster_id = createDiv('cluster_id',
          parent_div = cluster_id_column);

  var selected_cluster_row = createDivWithClass(null, 'row',
          parent_div = cluster_selector_panel_body);
  var selected_cluster_row = createDivWithClass(null, 'col-md-10',
          parent_div = selected_cluster_row,
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

  var instances_panel_body = createPanel('panel-primary', 'col-md-6',
                                     'Instances in Selected Cluster',
                                     row);
  // Tabs menu
  var menu_labels = ['instances_by_position',
                     'instances_by_label'];
  var menu_titles = ['Position', 'Label'];
  var menu = createTabsMenu(menu_labels, menu_titles,
          parent_div = instances_panel_body);
  // Tabs content
  var tabs_content = createDivWithClass(
          'cluster_instances_content',
          'tab-content',
          parent_div = instances_panel_body);
  // By position
  var by_position = createDivWithClass(
          'instances_by_position',
          'tab-pane fade in active',
          parent_div = tabs_content);
  // By label
  var by_label = createDivWithClass(
          'instances_by_label',
          'tab-pane fade',
          parent_div = tabs_content);

  // Third row
  var row = createDivWithClass(null,  'row', parent_div = main);
  // TODO update depending on use of clustering, annotation = true/false
  displayInstancePanel(row, annotation = false);
  displayInstanceInformationStructure();
  // TODO update depending on use of clustering
  //displayAnnotationDiv();
}

function createPerLabelSelectors(labels_families) {
  var instances_div = cleanDiv('instances_by_label');
  var labels_column = createDivWithClass('None', 'col-md-6',
                  parent_div = instances_div);
  var select_labels = createSelectList('select_labels',
                  5, null, labels_column,
                  label = labels_families);
  var instances_column = createDivWithClass('None',
                  'col-md-6',
                  parent_div = instances_div);
  var select_instances = createSelectList(
                  'select_instances_label_family',
                  5,
                  function() {
                    selected_instance_id = getSelectedOption(this);
                    printInstanceInformation(selected_instance_id, '');
                    last_instance_selector = this;
                  },
                  instances_column,
                  label = 'Instances');
}
