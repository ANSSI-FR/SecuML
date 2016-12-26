var project       = window.location.pathname.split('/')[2];
var dataset       = window.location.pathname.split('/')[3];
var experiment_id = window.location.pathname.split('/')[4];
var iteration     = window.location.pathname.split('/')[5];

var args = [project, dataset, experiment_id, iteration];

displayRadioButtons('barplot', args);

function displayRadioButtons(div_name, args) {
  var global_div = cleanDiv(div_name);
  var radio_name = 'radio';
  var radio_div = createDiv(radio_name, parent_div = global_div);
  var graph_div_name = 'graph_div';
  var graph_div = createDiv(graph_div_name, parent_div = global_div);
  function callback(label) {
    return function() {
      displaySublabels(args, label);
    }
  }
  var radio_benign = makeRadioButton(radio_name,
          'malicious', 'Malicious', true,
          callback('malicious'),
          parent_div = radio_div);
  var radio_benign = makeRadioButton(radio_name,
          'benign', 'Benign', false,
          callback('benign'),
          parent_div = radio_div);
  displaySublabels(args, 'malicious');
}

function displaySublabels(args, label) {
    if (!iteration) {
        // No iteration selected
        return;
    }
    var graph_div_name = 'graph_div';
    graph_div = cleanDiv(graph_div_name);
    var path = buildQuery('getSublabelsBarplot', args.concat([label]));
    drawBarPlotFromPath(graph_div_name,
                    path,
                    'Families',
                    'Num Annotations',
                    false,
                    null,
                    width = '1200',
                    height = '800');
}
