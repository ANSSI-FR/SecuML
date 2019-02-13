function generateClusteringDivisions() {
  var title = 'Clustering';
  if (conf.core_conf) {
      if (conf.core_conf.algo) {
        title += ' - ' + conf.core_conf.algo;
      }
  }
  generateTitle(title);

  var main = $('#main')[0];

  // First row
  var row = createDivWithClass(null, 'row', main);
  var num_instances_panel_body = createCollapsingPanel('panel-primary',
                                                       'col-md-6',
                                                       'Clusters Statistics',
                                                       row, null);
  var clusters_labels_stats = createDiv('clusters_labels_stats',
                                        parent_div=num_instances_panel_body);
  // Second row
  var row = createDivWithClass(null, 'row', main);

  var cluster_selector_panel_body = createPanel('panel-primary', 'col-md-3',
                                     'Select a Cluster',
                                     row);
  var cluster_id_column = createDivWithClass(null, 'row',
          parent_div=cluster_selector_panel_body);
  cluster_id_column = createDivWithClass(null, 'col-md-10',
          parent_div=cluster_id_column);
  var cluster_id = createDiv('cluster_id',
          parent_div=cluster_id_column);

  var selected_cluster_row = createDivWithClass(null, 'row',
          parent_div=cluster_selector_panel_body);
  var selected_cluster_row = createDivWithClass(null, 'col-md-10',
          parent_div=selected_cluster_row,
          title = 'Selected Cluster');

  var selected_cluster_info = createDiv('selected_cluster_info',
                                        parent_div=selected_cluster_row);
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
                            parent_div=instances_panel_body);
  // Tabs content
  var tabs_content = createDivWithClass('cluster_instances_content',
                                        'tab-content',
                                        parent_div=instances_panel_body);
  // By position
  var by_position = createDivWithClass('instances_by_position',
                                       'tab-pane fade in active',
                                       parent_div=tabs_content);
  // By label
  var by_label = createDivWithClass('instances_by_label',
                                    'tab-pane fade',
                                    parent_div=tabs_content);

  // Third row
  var row = createDivWithClass(null,  'row', parent_div=main);
  displayInstancePanel(row, annotation=true);
  displayInstanceInformationStructure();
  displayAnnotationDiv();
}

function createPerLabelSelectors(labels_families) {
  var instances_div = cleanDiv('instances_by_label');
  var labels_column = createDivWithClass('None', 'col-md-6',
                                         parent_div=instances_div);
  var select_labels = createSelectList('select_labels', 5, null, labels_column,
                                       label=labels_families);
  var instances_column = createDivWithClass('None', 'col-md-6',
                                            parent_div=instances_div);
  var select_instances = createSelectList('select_instances_label_family',
                  5,
                  function() {
                    selected_instance_id = getSelectedOption(this);
                    printInstanceInformation(selected_instance_id, '');
                    last_instance_selector = this;
                  },
                  instances_column,
                  label = 'Instances');
}
