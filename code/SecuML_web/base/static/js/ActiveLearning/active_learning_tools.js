function getNumIterations(conf) {
    var xmlHttp = new XMLHttpRequest();
    var query = buildQuery('getNumIterations',
                           [conf.project, conf.dataset, conf.experiment_id]);
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var num_iterations = xmlHttp.responseText;
    return parseInt(num_iterations);
}

function displayIterationSelector(conf) {
  var num_iterations = getNumIterations(conf);
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
