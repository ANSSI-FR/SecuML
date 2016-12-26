function displayAnnotationQueries(args, iteration, conf) {
  var div_object = cleanDiv('predicted_labels');
  var row = createDivWithClass('clustering_row', 'row');
  var results = document.createElement('button');
  var results_text = document.createTextNode('Annotating');
  results.appendChild(results_text);
  results.addEventListener('click', function() {
      if (conf.labeling_method == 'ILAB') {
        var query = buildQuery('activeLearningAnnotationsMenu',
            [project, dataset, experiment_id, iteration]);
      } else if(conf.labeling_method == 'random_sampling') {
        var query = buildQuery('individualAnnotations',
            [project, dataset, experiment_id,
            iteration, 'random']);
      } else if(conf.labeling_method == 'Cesa_Bianchi') {
        var query = buildQuery('individualAnnotations',
            [project, dataset, experiment_id,
            iteration, 'CesaBianchi']);
      } else {
        var query = buildQuery('individualAnnotations',
            [project, dataset, experiment_id,
            iteration, 'unsure']);
      }
      window.open(query);
  });
  row.appendChild(results);
  div_object.appendChild(row);
}
