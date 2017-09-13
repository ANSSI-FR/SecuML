function drawComponentsErrorEvolution(projection_type, experiment) {

  if (projection_type == 'Pca') {
    function get_path() {
      var graph_select = $('#projection_error_select')[0];
      var graph = graph_select.options[graph_select.selectedIndex].value;
      switch(graph) {
        case 'explained_variance':
          var projection_error_file = buildQuery('getExplVar', [experiment]);
          break;
        case 'cumuled_explained_variance':
          var projection_error_file = buildQuery('getCumExplVar', [experiment]);
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
          var error_recons_file = buildQuery('getReconsErrors', [experiment]);
          return error_recons_file; },
        'Components',
        function() { return 'reconstruction_errors'; },
        function() { return false; });
  }
}
