function displayPerformanceRadio(div_name, args, train_test, subkind = 'None') {
  var global_div = cleanDiv(div_name);
  var radio_name = train_test + '_radio_performance';
  var radio_div = createDiv(radio_name);
  var perf_div_name = train_test + '_perf_graph_div';
  var perf_div = createDiv(perf_div_name);
  global_div.appendChild(radio_div);
  global_div.appendChild(perf_div);
  function callback() {
    var iteration = getIteration();
    displayPerformance(args, iteration, train_test, subkind);
  }
  var radio_indicators = makeRadioButton(radio_name,
          train_test + '_indicators', 'Indicators', true,
          callback);
  radio_div.appendChild(radio_indicators);
  if (train_test != 'labels') {
    var radio_ROC = makeRadioButton(radio_name,
            train_test + '_ROC', 'ROC', false,
            callback);
    radio_div.appendChild(radio_ROC);
  }
  var radio_confusion_matrix = makeRadioButton(radio_name,
          train_test + '_confusion_matrix', 'Confusion Matrix', false,
          callback);
  radio_div.appendChild(radio_confusion_matrix);
}

function displayPerformance(args, iteration, train_test, subkind = 'None') {
    if (!iteration) {
        // No iteration selected
        return;
    }
    var perf_div_name = train_test + '_perf_graph_div';
    perf_div = cleanDiv(perf_div_name);
    var radio_indicators = $('#radio_' + train_test + '_indicators')[0];
    var radio_ROC = $('#radio_' + train_test + '_ROC')[0];
    var radio_confusion_matrix = $('#radio_' + train_test + '_confusion_matrix')[0];
    if (radio_indicators.checked) {
        displayPerfIndicators(perf_div_name, args, iteration, train_test, subkind);
    } else if (train_test != 'labels' && radio_ROC.checked) {
        displayROC(perf_div, args, iteration, train_test);
    } else if (radio_confusion_matrix.checked) {
        displayConfusionMatrix(perf_div_name, args, iteration,
                        train_test, subkind);
    }
}

function sliderCallback(train_test, iteration, subkind, event, ui) {
  return function(event, ui) {
    var threshold_col = cleanDiv('threshold_col_' + train_test);
    var value = $('#slider_' + train_test).slider('value');
    threshold_col.appendChild(document.createTextNode('Detection threshold: ' + value + '%'));
    var train_performance_path = buildQuery('getPerformanceIndicators',
            args.concat([iteration, train_test, subkind]));
    d3.json(train_performance_path, function(error, data) {
        fields_names = ['recall', 'false_positive', 'f-score'];
        var table = $('#perf_ind_table_' + train_test)[0];
        for (var i = 0; i < fields_names.length; i++) {
            field_name = fields_names[i]
            mean_cell = table.rows[i+1].cells[1];
            std_cell = table.rows[i+1].cells[2];
            mean_cell.innerHTML = data.thresholds[value][field_name].mean;
            if (train_test == 'cv') {
              std_cell.innerHTML = data.thresholds[value][field_name].std;
            }
        }
    });
  }
}

function displayPerfIndicators(div_name, args, iteration, train_test, subkind = 'None') {
  var train_performance_path = buildQuery('getPerformanceIndicators',
          args.concat([iteration, train_test, subkind]));
  // Slider to select the detectino threshold
  div_obj = $('#' + div_name)[0];
  var slider_row = createDivWithClass('slider_row_' + train_test, 'row', parent_div = div_obj);
  var threshold_col = createDivWithClass('threshold_col_' + train_test, 'col-md-4', parent_div = slider_row);
  threshold_col.appendChild(document.createTextNode('Detection threshold: 50%'));
  var slider_col = createDivWithClass('slider_col_' + train_test, 'col-md-4', parent_div = slider_row);
  createDiv('slider_' + train_test, parent_div = slider_col);
  $( function() {
    $('#slider_' + train_test).slider({
        min:0,
        max: 100,
        value: 50,
        range: 'max',
        change: sliderCallback(train_test, iteration, subkind)
    });
  });
  if (train_test == 'cv') {
    var table = createTable(div_name, ['Indicator', 'Mean', 'Std'],
            table_id = 'perf_ind_table_' + train_test);
    table.setAttribute('style','width:250px');
  } else {
    var table = createTable(div_name, ['Indicator', 'Value'],
            table_id = 'perf_ind_table_' + train_test);
    table.setAttribute('style','width:250px');
  }
  d3.json(train_performance_path, function(error, data) {
      if (train_test == 'labels') {
        fields_names = ['recall', 'false_positive', 'f-score'];
        fields_names_display = ['Detection', 'False alarms', 'F-score'];
      } else {
        fields_names = ['recall', 'false_positive', 'f-score', 'auc'];
        fields_names_display = ['Detection', 'False alarms', 'F-score', 'AUC'];
      }
      for (var i = 0; i < fields_names.length; i++) {
          var row = table.insertRow(i+1);
          var cell = row.insertCell(0);
          cell.innerHTML = fields_names_display[i];
          var cell = row.insertCell(1);
          field_name = fields_names[i]
          if (field_name == 'auc') {
            cell.innerHTML = data.auc.mean;
          } else {
            cell.innerHTML = data.thresholds[50][field_name].mean;
          }
          if (train_test == 'cv') {
            var cell = row.insertCell(2);
            if (field_name == 'auc') {
              cell.innerHTML = data.auc.std;
            } else {
              cell.innerHTML = data.thresholds[50][field_name].std;
            }
          }
      }
  });
}

function displayConfusionMatrix(div_name, args, iteration, train_test, subkind) {
    var benign_label = 'ok';
    var malicious_label = 'alert';
    var confusion_matrix_path = buildQuery('getConfusionMatrix',
            args.concat([iteration, train_test, subkind]));
    var table = createTable(div_name, 
                    ['', '', malicious_label, benign_label]);
    table.setAttribute('style','width:250px');
    var experiment_label_id = getExperimentLabelId(
            args[0], args[1], args[2]);
    d3.json(confusion_matrix_path, function(error, data) {

      var row = table.insertRow(0);
      var cell = row.insertCell(0);
      cell.innerHTML = '';
      var cell = row.insertCell(1);
      cell.innerHTML = '';
      var cell = row.insertCell(2);
      cell.colSpan = '2';
      cell.align = 'center';
      cell.innerHTML = 'Predicted Label';

      var row = table.insertRow(2);
      var cell = row.insertCell(0);
      cell.innerHTML = 'True Labels';
      cell.rowSpan = '2';
      cell.style.verticalAlign = 'middle';

      var cell = row.insertCell(1);
      cell.innerHTML = malicious_label;
      var cell = row.insertCell(2);
      cell.innerHTML = data['TP'];
      var cell = row.insertCell(3);
      var fn_elem = document.createElement('a');
      var fn_text = document.createTextNode(data['FN']);
      fn_elem.appendChild(fn_text);
      fn_elem.href = buildQuery('errors',
          args.concat([iteration, train_test, experiment_label_id]));
      cell.appendChild(fn_elem);
      cell.id = 'FN';

      var row = table.insertRow(3);
      var cell = row.insertCell(0);
      cell.innerHTML = benign_label;
      var cell = row.insertCell(1);
      var fp_elem = document.createElement('a');
      var fp_text = document.createTextNode(data['FP']);
      fp_elem.appendChild(fp_text);
      fp_elem.href = buildQuery('errors',
          args.concat([iteration, train_test, experiment_label_id]));
      cell.appendChild(fp_elem);
      cell.id = 'FP';
      var cell = row.insertCell(2);
      cell.innerHTML = data['TN'];
    });
}

function displayROC(div, args, iteration, train_test) {
  var ROC_path = buildQuery('getRoc',
          args.concat([iteration, train_test]));
  var picture = document.createElement('img');
  picture.src = ROC_path;
  picture.style.width = '80%';
  picture.style.height = 'auto';
  div.appendChild(picture);
}
