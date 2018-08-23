function displayAnnotationQueries(conf, iteration) {
  var div_object = cleanDiv('predicted_labels');
  var row = createDivWithClass('clustering_row', 'row');
  var results = document.createElement('button');
  results.setAttribute('class', 'btn btn-primary');
  var results_text = document.createTextNode('Annotating');
  results.appendChild(results_text);
  results.addEventListener('click', function() {
      if (conf.query_strategy == 'Ilab') {
        var query = buildQuery('ilabAnnotations',
            [experiment_id, iteration]);
      } else if(conf.query_strategy == 'RareCategoryDetection') {
        var query = buildQuery('rareCategoryDetectionAnnotations',
            [experiment_id, iteration]);
      } else {
        var query = buildQuery('individualAnnotations',
            [experiment_id, iteration]);
      }
      window.open(query);
  });
  row.appendChild(results);
  div_object.appendChild(row);
}
