function displaySettings(conf) {
  var body = createTable('settings', ['', ''], width = 'width:280px');

  // Project Dataset
  addRow(body, ['Project', conf.dataset_conf.project]);
  addRow(body, ['Dataset', conf.dataset_conf.dataset]);

  // Classifier
  if (conf.classification_conf) {
    var classification_conf = conf.classification_conf;
    var model_class = classification_conf['__type__'].split(
            'Configuration')[0];
    var num_folds = classification_conf.num_folds;
    addRow(body, ['Model Class', model_class]);
    addRow(body, ['Num folds', num_folds]);
  }

  // Labeling Method
  addRow(body, ['Labeling Strategy', conf.query_strategy]);

  // Rare Category Detection Configuration
  if (conf.query_strategy == 'Ilab' || conf.query_strategy == 'RareCategoryDetection') {
      var classification_conf = conf.core_conf.rcd_conf.classification_conf;
      var model = classification_conf.classifier_conf.__type__.split('Conf')[0];
      addRow(body, ['Model', model]);
  }
}

function displayLabelsInformation(exp_id, iteration) {
  // Labels stats
  var stats_div = cleanDiv('stats');
  var path = buildQuery('getLabelsMonitoring', [exp_id, iteration]);
  d3.json(path, function(data) {
    var ul = document.createElement('ul');
    ul.setAttribute('class', 'list-group');
    var keys = ['annotations', 'unlabeled'];
    var keys_labels = ['annotations', 'unlabeled instances'];
    for (var i in keys) {
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
  var buttons_div = createDivWithClass(null, 'btn-group btn-group-justified',
                                       check_annotations_div);
  var button = document.createElement('a');
  button.setAttribute('class', 'btn btn-default')
  button.appendChild(document.createTextNode('Annotated Instances'));
  button.addEventListener('click', function() {
    var path = buildQuery('currentAnnotations', [exp_id, iteration]);
    window.open(path);
  });
  buttons_div.appendChild(button);
  // Edit families
  var edit_families_div = cleanDiv('edit_families');
  var buttons_div = createDivWithClass(null, 'btn-group btn-group-justified', edit_families_div);
  var button = document.createElement('a');
  button.setAttribute('class', 'btn btn-default');
  button.appendChild(document.createTextNode('Family Editor'));
  button.addEventListener('click', function() {
    var path = buildQuery('editFamilies', [exp_id]);
    window.open(path);
  });

  buttons_div.appendChild(button);
}
