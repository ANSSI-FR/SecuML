function displaySettings(conf) {
  var table = createTable('settings',
      ['', '']);
  table.setAttribute('style','width:280px');
  // Project Dataset
  var row = table.insertRow(1);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Project';
  var cell = row.insertCell(1);
  cell.innerHTML = project;
  var row = table.insertRow(2);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Dataset';
  var cell = row.insertCell(1);
  cell.innerHTML = dataset;
  if (hide_confidential) {
    cell.innerHTML = '';
  }
  // Supervised Learning
  var supervised_learning_conf = conf.supervised_learning_conf;
  var row = table.insertRow(3);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Model Class';
  var cell = row.insertCell(1);
  cell.innerHTML = supervised_learning_conf['__type__'].split('Configuration')[0];
  var row = table.insertRow(4);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Sample Weights';
  var cell = row.insertCell(1);
  cell.innerHTML = supervised_learning_conf.sample_weight;

  var row = table.insertRow(5);
  var cell = row.insertCell(0);
  cell.innerHTML = 'Labeling Procedure';
  var cell = row.insertCell(1);
  cell.innerHTML = conf.labeling_method;
  // Ilab Configuration
  if (conf.labeling_method == 'ILAB') {
      var ilab_conf = conf.ilab_conf
      var row = table.insertRow(6);
      var cell = row.insertCell(0);
      cell.innerHTML = 'Semi-auto labels';
      var cell = row.insertCell(1);
      cell.innerHTML = ilab_conf.semiauto;
      var row = table.insertRow(7);
      var cell = row.insertCell(0);
      cell.innerHTML = 'Clustering';
      var cell = row.insertCell(1);
      cell.innerHTML = ilab_conf.clustering_conf['__type__'].split('Configuration')[0];
      var row = table.insertRow(8);
      var cell = row.insertCell(0);
      cell.innerHTML = 'Projection';
      var proj = ilab_conf.clustering_conf.projection_conf;
      var cell = row.insertCell(1);
      if (proj) {
        cell.innerHTML = proj['__type__'].split('Configuration')[0];
      } else {
        cell.innerHTML = 'None';
      }
  }
}

function displayLabelsInformation(args, iteration) {
  var stats_div = cleanDiv('stats');
  var path = buildQuery('getLabelsMonitoring', args.concat([iteration]));
  d3.json(path, function(error, data) {
    var ul = document.createElement('ul');
    keys = ['unlabeled', 'annotations'];
    for (i in keys) {
        k = keys[i];
        var li = document.createElement('li');
        var text = data[k] + ' ' + k;
        var text = document.createTextNode(text);
        li.appendChild(text);
        ul.appendChild(li);
    }
    stats_div.appendChild(ul);
  });
  var sublabels_link = document.createElement('a');
  sublabels_link.appendChild(document.createTextNode('Sublabels'));
  var path = buildQuery('sublabels', args.concat([iteration]));
  sublabels_link.href = path;
  stats_div.appendChild(sublabels_link);
}
