var project       = window.location.pathname.split('/')[2];
var dataset       = window.location.pathname.split('/')[3];
var experiment_id = window.location.pathname.split('/')[4];
var train_test    = window.location.pathname.split('/')[5];

function sliderCallback(event, ui) {
  return function(event, ui) {
    var threshold_col = cleanDiv('threshold');
    var value = $('#slider').slider('value');
    threshold_col.appendChild(document.createTextNode('Detection threshold: ' + value + '%'));
    displayFamiliesPerformance(project, dataset, experiment_id, train_test, 'malicious');
    displayFamiliesPerformance(project, dataset, experiment_id, train_test, 'benign');
  }
}

// Draw slider
var threshold_col = cleanDiv('threshold');
threshold_col.appendChild(document.createTextNode(
            'Detection threshold: 50%'));
$( function() {
  $('#slider').slider({
      min:0,
      max: 100,
      value: 50,
      range: 'max',
      change: sliderCallback()
  });
  displayFamiliesTabs('barplot', project, dataset, experiment_id, train_test);
});
