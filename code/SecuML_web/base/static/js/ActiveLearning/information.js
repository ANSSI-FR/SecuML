function displaySettings(conf) {
  var body = createTable('settings', ['', ''], width = 'width:280px');

  // Project Dataset
  addRow(body, ['Project', project]);
  addRow(body, ['Dataset', dataset]);

  // Classifier
  if (conf.classification_conf) {
    var classification_conf = conf.classification_conf;
    var model_class = classification_conf['__type__'].split(
            'Configuration')[0];
    var num_folds = classification_conf.num_folds;
    var sample_weight = classification_conf.sample_weight;
    addRow(body, ['Model Class', model_class]);
    addRow(body, ['Num folds', num_folds]);
    addRow(body, ['Sample Weights', sample_weight]);
  }

  // Labeling Method
  var labeling_method = conf.labeling_method;
  addRow(body, ['Labeling Strategy', labeling_method]);

  // Rare Category Detection Configuration
  if (labeling_method == 'Ilab' || labeling_method == 'RareCategoryDetection') {
      var semi_auto_labels = conf.conf.rare_category_detection_conf.semiauto;
      var clustering_conf = conf.conf.rare_category_detection_conf.clustering_conf;
      var clustering = clustering_conf['__type__'].split('Configuration')[0];
      var projection = clustering_conf.projection_conf;
      if (projection) {
        projection= projection['__type__'].split('Configuration')[0];
      } else {
        projection = 'None';
      }
      addRow(body, ['Semi-auto labels', semi_auto_labels]);
      addRow(body, ['Clustering', clustering]);
      addRow(body, ['Projection', projection]);
  }
}

function displayLabelsInformation(project, dataset, experiment_id, iteration) {
  // Labels stats
  var stats_div = cleanDiv('stats');
  var path = buildQuery('getLabelsMonitoring', [project, dataset, experiment_id, iteration]);
  d3.json(path, function(error, data) {
    var ul = document.createElement('ul');
    ul.setAttribute('class', 'list-group');
    var keys = ['annotations', 'unlabeled'];
    var keys_labels = ['annotations', 'unlabeled instances'];
    for (i in keys) {
        k = keys[i];
        l = keys_labels[i];
        var li = document.createElement('li');
        var text = data[k] + ' ' + l;
        var text = document.createTextNode(text);
        li.appendChild(text);
        ul.appendChild(li);
    }
    stats_div.appendChild(ul);
  });
  // Check annotations
  var check_annotations_div = cleanDiv('check_annotations')
  var buttons_div = createDivWithClass(null, 'btn-group btn-group-justified', check_annotations_div);
  var labels_button = document.createElement('a');
  labels_button.setAttribute('class', 'btn btn-default')
  labels_button.appendChild(document.createTextNode('Labels'));
  var experiment_label_id = getExperimentLabelId(project, dataset, experiment_id);
  var path = buildQuery('labeledInstances', [project, dataset, experiment_id, experiment_label_id, iteration]);
  labels_button.href = path;
  buttons_div.appendChild(labels_button);

  var families_button = document.createElement('a');
  families_button.setAttribute('class', 'btn btn-default')
  families_button.appendChild(document.createTextNode('Families'));
  var path = buildQuery('families', [project, dataset, experiment_id, iteration]);
  families_button.href = path;
  buttons_div.appendChild(families_button);
}
