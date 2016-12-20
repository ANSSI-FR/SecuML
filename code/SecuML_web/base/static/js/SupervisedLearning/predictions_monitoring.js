function displayPredictionsRadio(div_name, args, conf, train_test) {
  var global_div = cleanDiv(div_name);
  var radio_name =  train_test + '_radio_predictions_hist_density';
  var radio_div = createDiv(radio_name);
  var predictions_div_name = train_test + '_predictions_graph';
  var predictions_div = createDiv(predictions_div_name);
  global_div.appendChild(radio_div);
  global_div.appendChild(predictions_div);
  if (validationWithoutTrueLabels(train_test, conf, exp_type)) {
      return;
  }
  function callback() {
    var iteration = getIteration();
    displayPredictions(args, iteration, conf, train_test);
  }
  var radio_histogram = makeRadioButton(radio_name,
          train_test + '_predictions_histogram', 'Histogram', true,
          callback);
  var radio_density = makeRadioButton(radio_name,
          train_test + '_predictions_density', 'Density', false,
          callback);
  radio_div.appendChild(radio_histogram);
  radio_div.appendChild(radio_density);
}

function displayPredictions(args, iteration, conf, train_test) {
    if (!iteration) {
        // No iteration selected
        return;
    }
    var predictions_div_name =  train_test + '_predictions_graph';
    predictions_div = cleanDiv(predictions_div_name);
    if (validationWithoutTrueLabels(train_test, conf, exp_type)) {
        displayPredictionsBarplot(predictions_div_name,
                        args, iteration, conf, train_test);
        return;
    }
    var radio_histogram = $('#radio_' + train_test + '_predictions_histogram')[0];
    var radio_density = $('#radio_' + train_test + '_predictions_density')[0];
    if (radio_histogram.checked) {
        displayPredictionsBarplot(predictions_div_name,
                        args, iteration, conf, train_test);
    } else if (radio_density.checked) {
        displayPredictionsDensity(predictions_div_name,
                        args, iteration, train_test);
    }
}

function displayPredictionsBarplot(div_name, args, iteration, conf, train_test) {
  cleanDiv(train_test + '_predictions_graph');
  if (validationWithoutTrueLabels(train_test, conf, exp_type)) {
    var get_function = 'getPredictionsBarplot';
  } else {
    var get_function = 'getPredictionsBarplotLabels';
  }
  var path = buildQuery(get_function,
          args.concat([iteration, train_test]));
  drawBarPlotFromPath(div_name,
                  path,
                  'Proba',
                  'numInstances',
                  false,
                  null);
}

function displayPredictionsDensity(div_name, args, iteration, train_test) {
  cleanDiv(train_test + '_predictions_graph');
  var density_path = buildQuery('getPredictionsDensityPNG',
          args.concat([iteration, train_test]));
  var div = cleanDiv(div_name);
  var picture = document.createElement('img');
  picture.src = density_path;
  picture.style.width = '80%';
  picture.style.height = 'auto';
  div.appendChild(picture);
}
