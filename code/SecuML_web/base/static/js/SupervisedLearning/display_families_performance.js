var project       = window.location.pathname.split('/')[2];
var dataset       = window.location.pathname.split('/')[3];
var experiment_id = window.location.pathname.split('/')[4];
var iteration     = window.location.pathname.split('/')[5];
var train_test    = window.location.pathname.split('/')[6];

var args = [project, dataset, experiment_id];

function sliderCallback(event, ui) {
  return function(event, ui) {
    var threshold_col = cleanDiv('threshold');
    var value = $('#slider').slider('value');
    threshold_col.appendChild(document.createTextNode('Detection threshold: ' + value + '%'));
    displayFamiliesPerformance(args, iteration, train_test);
  }
}

// Draw slider
var threshold_col = cleanDiv('threshold');
threshold_col.appendChild(document.createTextNode('Detection threshold: 50%'));
$( function() {
  $('#slider').slider({
      min:0,
      max: 100,
      value: 50,
      range: 'max',
      change: sliderCallback()
  });
  displayFamiliesRadio('barplot', [project, dataset, experiment_id], iteration, train_test);
});
