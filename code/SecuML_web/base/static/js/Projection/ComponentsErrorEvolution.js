function drawComponentsErrorEvolution(project, dataset, projection_type,
        experiment) {

  if (projection_type == 'Pca') {
    function get_path() {
      var graph_select = $('#projection_error_select')[0];
      var graph = graph_select.options[graph_select.selectedIndex].value;
      var args = [project, dataset, experiment];
      switch(graph) {
        case 'explained_variance':
          var projection_error_file = buildQuery('getExplVar', args);
          break;
        case 'cumuled_explained_variance':
          var projection_error_file = buildQuery('getCumExplVar', args);
          break;
      }
      return projection_error_file;
    }

    function get_ylabel() {
      var graph_select = $('#projection_error_select')[0];
      var graph = graph_select.options[graph_select.selectedIndex].value
        return graph;
    }

    addCallBackOnPlotSelectList('projection_error_graph',
        get_path,
        'projection_error_select',
        'Components',
        get_ylabel,
        function() { return true; });

  } else {
    drawPlot('projection_error_graph',
        function() {
          var error_recons_file = buildQuery('getReconsErrors', args);
          return error_recons_file; },
        'Components',
        function() { return 'reconstruction_errors'; },
        function() { return false; });
  }
}
