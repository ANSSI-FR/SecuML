function loadFamiliesPage(args, iteration, train_test) {
    var query = buildQuery('familiesPerformance',
            args.concat([iteration, train_test]));
    window.open(query);
}

function displayFamiliesRadio(div_name, args, iteration, train_test, subkind = 'None') {
  var global_div = cleanDiv(div_name);
  var radio_name = train_test + '_radio_families';
  var radio_div = createDiv(radio_name, parent_div = global_div);
  var perf_div_name = train_test + '_perf_graph_div';
  var perf_div = createDiv(perf_div_name, parent_div = global_div);
  function callback() {
    displayFamiliesPerformance(args, iteration, train_test, subkind);
  }
  var radio_benign = makeRadioButton(radio_name,
          train_test + 'families_malicious', 'Malicious', true,
          callback,
          parent_div = radio_div);
  var radio_benign = makeRadioButton(radio_name,
          train_test + 'families_benign', 'Benign', false,
          callback,
          parent_div = radio_div);
  displayFamiliesPerformance(args, iteration, train_test);
}

function displayFamiliesPerformance(args, iteration, train_test, subkind = 'None') {
    if (!iteration) {
        // No iteration selected
        return;
    }
    var threshold = $('#slider').slider('value');
    var perf_div_name = train_test + '_perf_graph_div';
    perf_div = cleanDiv(perf_div_name);
    var label = 'benign';
    var radio_malicious = $('#radio_' + train_test + 'families_malicious')[0];
    if (radio_malicious.checked) {
        label = 'malicious';
    }
    var path = buildQuery('getFamiliesPerformance', args.concat([iteration, train_test, label, threshold]));
    drawBarPlotFromPath(perf_div_name,
                    path,
                    'Families',
                    'Performance',
                    false,
                    null,
                    width = '1200',
                    height = '800');
}

function displayFamiliesMonitoring(args, iteration, train_test) {
  var div = cleanDiv(train_test + '_monitoring');
  var path = buildQuery('getFamiliesRoc',
          args.concat([iteration, train_test]));
  var picture = document.createElement('img');
  picture.src = path;
  picture.style.width = '80%';
  picture.style.height = 'auto';
  div.appendChild(picture);
  var button = document.createElement('button');
  var button_text = document.createTextNode('FP/TP');
  button.appendChild(button_text);
  button.addEventListener('click', function() {
      loadFamiliesPage(args, iteration, train_test);
  });
  div.appendChild(button);
}
