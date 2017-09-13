var path = window.location.pathname.split('/');
var experiment_id = path[2];
var train_test    = path[3];

function sliderCallback(event, ui) {
  return function(event, ui) {
    var threshold_col = cleanDiv('threshold');
    var value = $('#slider').slider('value');
    threshold_col.appendChild(document.createTextNode('Detection threshold: ' + value + '%'));
    displayFamiliesPerformance(experiment_id, train_test, 'malicious');
    displayFamiliesPerformance(experiment_id, train_test, 'benign');
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
  displayFamiliesTabs('barplot', experiment_id, train_test);
});
