function runNextIteration(conf) {
    return function() {
        // Generate the next annotation queries
        var query = buildQuery('runNextIteration',
                               [conf.experiment_id, label_iteration]);
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open('GET', query, false);
        xmlHttp.send(null);
        // Close the current tab
        window.close();
    }
}

function currentAnnotationIteration(experiment_id) {
    var xmlHttp = new XMLHttpRequest();
    var query = buildQuery('currentAnnotationIteration',
                           [experiment_id]);
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var current_iteration = xmlHttp.responseText;
    return parseInt(current_iteration);
}

function displayIterationSelector(conf, num_iterations) {
  iterations = [];
  for (var i = 1; i <= num_iterations; i++) {
    iterations.push(i);
  }
  addElementsToSelectList('iteration_selector', iterations);
  var iteration_selector = $('#iteration_selector')[0];
  iteration_selector.addEventListener('change', function() {
      return displayIteration(conf);
  });
  // The last iteration is automatically selected
  if (num_iterations >= 1) {
    iteration_selector.selectedIndex = num_iterations - 1;
  }
}

function getIteration() {
  if ('iteration' in window){
    return 'None';
  } else {
    var iteration_selector =
            $('#iteration_selector')[0];
    var iteration = getSelectedOption(iteration_selector);
    return iteration;
  }
}
