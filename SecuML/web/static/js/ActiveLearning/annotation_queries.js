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
      } else if(conf.query_strategy == 'RandomSampling') {
        var query = buildQuery('individualAnnotations',
            [experiment_id, iteration, 'random']);
      } else if(conf.query_strategy == 'CesaBianchi') {
        var query = buildQuery('individualAnnotations',
            [experiment_id, iteration, 'CesaBianchi']);
      } else if (conf.query_strategy == 'Aladin'){
        var query = buildQuery('individualAnnotations',
            [experiment_id, iteration, 'aladin']);
      } else {
        var query = buildQuery('individualAnnotations',
            [experiment_id, iteration, 'uncertain']);
      }
      window.open(query);
  });
  row.appendChild(results);
  div_object.appendChild(row);
}
