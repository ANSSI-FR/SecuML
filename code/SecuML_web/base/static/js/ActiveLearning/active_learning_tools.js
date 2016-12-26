function addCheckLabelsButton(project, dataset, experiment_label_id) {
    var div = $('#check_labels_div')[0];
    var button = document.createElement('button');
    var button_text = document.createTextNode('Check Labels');
    button.appendChild(button_text);
    var label_iteration = getIteration();
    if (!label_iteration) {
        label_iteration = 0;
    }
    button.addEventListener('click', function() {
        var query = buildQuery('labeledInstances',
                [project, dataset, experiment_label_id, label_iteration]);
        window.open(query);
    });
    div.appendChild(button)
}

function getNumIterations(args) {
    var xmlHttp = new XMLHttpRequest();
    var query = buildQuery('getNumIterations', args);
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var num_iterations = xmlHttp.responseText;
    return parseInt(num_iterations);
}

function displayIterationSelector(args, conf) {
  var num_iterations = getNumIterations(args);
  iterations = [];
  for (var i = 1; i <= num_iterations; i++) {
    iterations.push(i);
  }
  addElementsToSelectList('iteration_selector', iterations);
  var iteration_selector = $('#iteration_selector')[0];
  iteration_selector.addEventListener('change', function() {
      return displayIteration(args, conf)
  });
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
