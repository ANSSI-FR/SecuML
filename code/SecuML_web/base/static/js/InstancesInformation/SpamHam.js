var last_selected_id = null;

function displayInformationStructure() {
  function callback() {
    if (last_selected_id) {
        printInformation(last_selected_id);
    }
  }
}

function printInformation(selected_id, ident) {
  printMail(selected_id, ident);
}

function cleanInformation() {
    cleanDiv('instance_data_div');
}

function displayMailClusterInterpretation(num_clusters, selected_cluster) {
    var div_object = cleanDiv('clustering_display');
    var query = buildQuery('getClusterFeaturesVariance',
        args.concat([num_clusters, selected_cluster]));
    var table = createTable('clustering_display', ['Feature', 'Var']);
    table.setAttribute('style','width:100px');
    d3.csv(query, function(error, data) {
        var i = 0;
        data.forEach(function (d) {
            var row = table.insertRow(i+1);
            var cell = row.insertCell(0);
            cell.innerHTML = d['Feature'];
            var cell = row.insertCell(1);
            cell.innerHTML = d['Variance'];
            i++;
        });
    });
}

function printMail(selected_id, ident) {
  last_selected_id = selected_id;
  var div_object = cleanDiv('instance_data');
  var radio_features = $('#radio_features')[0];
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open('GET',
      buildQuery('getInstance',
              [project, inst_dataset, selected_id, ident]),
      false);
  xmlHttp.send(null);
  mail_text = xmlHttp.responseText;
  mail = document.createTextNode(mail_text);
  div_object.appendChild(mail);
}


function printNonNullFeatures(selected_id) {
  var div_object = cleanDiv('instance_data_div');
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open('GET',
      buildQuery('getFeatures',
              [project, experiment_dataset, experiment_label_id, validation_dataset, selected_id]),
      false);
  xmlHttp.send(null);
  var features = xmlHttp.responseText;
  features = features.split('|');
  var num_features = features.length;
  var ul = document.createElement('ul');
  for (var i = 0; i < num_features; i++) {
    var li = document.createElement('li');
    li.appendChild(document.createTextNode(features[i]));
    ul.appendChild(li);
  }
  div_object.appendChild(ul);
}
