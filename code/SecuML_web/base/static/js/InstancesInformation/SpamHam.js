function specificInformationStructure(radio_list) {
    radio_list.splice(0, 0, ['mail', 'Mail', true]);
}

function printSpecificData(selected_id, ident, selected_radio) {
    switch (selected_radio) {
        case 'mail':
            printMail(selected_id, ident);
            break;
    }
}

function cleanInstanceInformation() {
    cleanDiv('instance_data_div');
}

function displayMailClusterInterpretation(num_clusters, selected_cluster) {
    var div_object = cleanDiv('clustering_display');
    var query = buildQuery('getClusterFeaturesVariance',
        args.concat([num_clusters, selected_cluster]));
    var table = createTable('clustering_display', ['Feature', 'Var']);
    table.setAttribute('style', 'width:100px');
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
  var div_object = cleanDiv('instance_data_div');
  var query = buildQuery('getInstance',
              [project, inst_dataset, selected_id, ident]);
  $.get(query, function(data) {
      var mail = document.createTextNode(data);
      div_object.appendChild(mail);
  });
}
