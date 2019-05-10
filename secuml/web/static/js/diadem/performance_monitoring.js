function displayPerformanceTabs(train_test, exp_info) {
    var performance_div_name =  train_test + '_perf';
    if (exp_info.multiclass) {
      var menu_labels = [train_test + '_perf_indicators'];
      var menu_titles = ['Indicators'];
    } else {
      if (exp_info.proba || exp_info.with_scoring) {
        var menu_labels = [train_test + '_perf_indicators',
                           train_test + '_perf_curves',
                           train_test + '_confusion_matrix'];
        var menu_titles = ['Indicators', 'Curves', 'Matrix'];
      } else {
        var menu_labels = [train_test + '_perf_indicators',
                           train_test + '_confusion_matrix'];
        var menu_titles = ['Indicators', 'Matrix'];
      }
    }
    var menu = createTabsMenu(menu_labels, menu_titles,
            document.getElementById(performance_div_name),
            train_test + '_perf_monitoring_tabs');
    document.getElementById(performance_div_name).style.marginTop = '2px';
    if (!exp_info.multiclass && (exp_info.proba || exp_info.with_scoring)) {
        displayCurvesTabs(train_test);
    }
}

function displayCurvesTabs(train_test) {
    var curves_div_name =  train_test + '_perf_curves';
    var menu_labels = [train_test + '_roc',
                       train_test + '_far_tpr'];
    var menu_titles = ['ROC',
                       'FAR-DR'];
    var menu = createTabsMenu(menu_labels, menu_titles,
            document.getElementById(curves_div_name),
            train_test + '_perf_curves_tabs');
    document.getElementById(curves_div_name).style.marginTop = '2px';
}

function updatePerformanceDisplay(train_test, exp, proba, with_scoring,
                                  multiclass, with_links) {
    // Indicators
    var indicators = cleanDiv(train_test + '_perf_indicators');
    displayPerfIndicators(indicators, train_test, exp, proba, multiclass);
    if (!multiclass) {
      // ROC
      if (proba || with_scoring) {
        var roc = cleanDiv(train_test + '_roc');
        displayROC(roc, train_test, exp);
        var precision_recall = cleanDiv(train_test + '_far_tpr');
        displayPrecisionRecall(precision_recall, train_test, exp)
      }
      // Confusion Matrix
      var confusion_matrix = cleanDiv(train_test + '_confusion_matrix');
      displayConfusionMatrix(confusion_matrix, train_test, exp, with_links);
    }
}

function sliderCallback(train_test, sup_exp, event, ui) {
  return function(event, ui) {
    var threshold_col = cleanDiv('threshold_col_' + train_test);
    var value = $('#slider_' + train_test).slider('value');
    threshold_col.appendChild(document.createTextNode('Detection threshold: ' + value + '%'));
    var performance_path = buildQuery('supervisedLearningMonitoring',
                                      [sup_exp, 'perf_indicators']);
    $.getJSON(performance_path,
              function(data) {
                  fields_names = ['recall', 'false_positive', 'f-score'];
                  var table = $('#perf_ind_table_' + train_test)[0];
                  for (var i = 0; i < fields_names.length; i++) {
                      field_name = fields_names[i]
                      mean_cell = table.rows[i].cells[1];
                      std_cell = table.rows[i].cells[2];
                      mean_cell.innerHTML = data.thresholds[value][field_name].mean;
                      if (train_test == 'cv') {
                        std_cell.innerHTML = data.thresholds[value][field_name].std;
                      }
                  }
              }
             );
  }
}

function displayPerfIndicators(div_obj, train_test, exp, proba, multiclass) {
  if (proba && !multiclass) {
      displayThresholdPerfIndicators(div_obj, train_test, exp);
  } else {
      displayNoThresholdPerfIndicators(div_obj, train_test, exp, multiclass);
  }
}

function displayNoThresholdPerfIndicators(div_obj, train_test, exp, multiclass) {
  var train_performance_path = buildQuery('supervisedLearningMonitoring',
                                          [exp, 'perf_indicators']);
  var header = null;
  if (train_test == 'cv') {
      header = ['Indicator', 'Mean', 'Std'];
  }
  var body = createTable(div_obj.id, header,
                         table_id='perf_ind_table_' + train_test);
  $.getJSON(train_performance_path,
            function(data) {
                if (multiclass) {
                  var fields_names = ['f1_micro', 'f1_macro', 'accuracy'];
                  var fields_names_display = ['F1-micro', 'F1-macro', 'Accuracy'];
                } else {
                  var fields_names = ['recall', 'far', 'f-score', 'auc'];
                  var fields_names_display = ['Detection Rate',
                                              'False Alarm Rate',
                                              'F-score',
                                              'AUC'];
                }
                for (var i = 0; i < fields_names.length; i++) {
                    var indicator = fields_names_display[i];
                    var field_name =fields_names[i];
                    if (field_name == 'auc') {
                      var value = data.auc.mean;
                    } else {
                      var value = data[field_name].mean;
                    }
                    var elements = [indicator, value];
                    if (train_test == 'cv') {
                      if (field_name == 'auc') {
                        var std = data.auc.std;
                      } else {
                        var std = data[field_name].std;
                      }
                      elements.push(std);
                    }
                    addRow(body, elements, title=true);
                }
            }
           );
}

function displayThresholdPerfIndicators(div_obj, train_test, exp) {
  var train_performance_path = buildQuery('supervisedLearningMonitoring',
                                          [exp, 'perf_indicators']);
  // Slider to select the detection threshold
  var slider_row = createDivWithClass('slider_row_' + train_test, 'row',
                                      parent_div=div_obj);
  var threshold_col = createDivWithClass('threshold_col_' + train_test,
                                         'col-md-6', parent_div=slider_row);
  threshold_col.appendChild(document.createTextNode('Detection threshold: 50%'));
  var slider_col = createDivWithClass('slider_col_' + train_test, 'col-md-6',
                                      parent_div=slider_row);
  createDiv('slider_' + train_test, parent_div = slider_col);
  $( function() {
    $('#slider_' + train_test).slider({
        min:0,
        max: 100,
        value: 50,
        range: 'max',
        change: sliderCallback(train_test, exp)
    });
  });
  var header = null;
  if (train_test == 'cv') {
      header = ['Indicator', 'Mean', 'Std'];
  }
  var body = createTable(div_obj.id, header,
          table_id = 'perf_ind_table_' + train_test);
  $.getJSON(train_performance_path,
            function(data) {
                if (train_test == 'labels') {
                  fields_names = ['recall', 'far', 'f-score'];
                  fields_names_display = ['Detection Rate',
                                          'False Alarm Rate',
                                          'F-score'];
                } else {
                  fields_names = ['recall', 'far', 'f-score', 'auc'];
                  fields_names_display = ['Detection Rate',
                                          'False Alarm Rate',
                                          'F-score',
                                          'AUC'];
                }
                for (var i = 0; i < fields_names.length; i++) {
                    var indicator = fields_names_display[i];
                    var field_name =fields_names[i];
                    if (field_name == 'auc') {
                      var value = data.auc.mean;
                    } else {
                      var value = data.thresholds[50][field_name].mean;
                    }
                    var elements = [indicator, value];
                    if (train_test == 'cv') {
                      if (field_name == 'auc') {
                        var std = data.auc.std;
                      } else {
                        var std = data.thresholds[50][field_name].std;
                      }
                      elements.push(std);
                    }
                    addRow(body, elements, title = true);
                }
            }
           );
}

function displayConfusionMatrix(div_obj, train_test, exp, with_links) {
    var benign_label = 'ok';
    var malicious_label = 'alert';
    var confusion_matrix_path = buildQuery('supervisedLearningMonitoring',
                                           [exp, 'confusion_matrix']);
    var table = createTable(div_obj.id, null,
                    ['', '', malicious_label, benign_label],
                    table_id = null);
    $.getJSON(confusion_matrix_path,
              function(data) {

                var row = table.insertRow(0);
                var cell = row.insertCell(0);
                cell.innerHTML = '';
                var cell = row.insertCell(1);
                cell.innerHTML = '';
                var cell = row.insertCell(2);
                cell.colSpan = '2';
                cell.align = 'center';
                cell.innerHTML = 'Prediction';

                var row = table.insertRow(1);
                var cell = row.insertCell(0);
                cell.innerHTML = '';
                var cell = row.insertCell(1);
                cell.innerHTML = '';
                var cell = row.insertCell(2);
                cell.innerHTML = malicious_label;
                var cell = row.insertCell(3);
                cell.innerHTML = benign_label;

                var row = table.insertRow(2);
                var cell = row.insertCell(0);
                cell.innerHTML = 'Truth';
                cell.rowSpan = '2';
                cell.style.verticalAlign = 'middle';

                var cell = row.insertCell(1);
                cell.innerHTML = malicious_label;
                var cell = row.insertCell(2);
                cell.innerHTML = data['TP'];
                var cell = row.insertCell(3);
                if (with_links) {
                    var fn_elem = document.createElement('a');
                    var fn_text = document.createTextNode(data['FN']);
                    fn_elem.appendChild(fn_text);
                    var errors_query = buildQuery('errors', [exp, 'FN']);
                    fn_elem.href = errors_query;
                    fn_elem.setAttribute('title', 'False Negatives');
                    cell.appendChild(fn_elem);
                    cell.id = 'FN';
                } else {
                    cell.innerHTML = data['FN'];
                }
                var row = table.insertRow(3);
                var cell = row.insertCell(0);
                cell.innerHTML = benign_label;
                var cell = row.insertCell(1);
                if (with_links) {
                    var fp_elem = document.createElement('a');
                    var fp_text = document.createTextNode(data['FP']);
                    fp_elem.appendChild(fp_text);
                    var errors_query = buildQuery('errors', [exp, 'FP']);
                    fp_elem.href = errors_query;
                    fp_elem.setAttribute('title', 'False Positives');
                    cell.appendChild(fp_elem);
                    cell.id = 'FP';
                } else {
                    cell.innerHTML = data['FP'];
                }
                var cell = row.insertCell(2);
                cell.innerHTML = data['TN'];
    });
}

function displayROC(div, train_test, exp) {
  var ROC_path = buildQuery('supervisedLearningMonitoring', [exp, 'ROC']);
  var picture = document.createElement('img');
  picture.setAttribute('class', 'img-responsive');
  picture.src = ROC_path;
  div.appendChild(picture);
}

function displayPrecisionRecall(div, train_test, exp) {
  var precision_recall_path = buildQuery('supervisedLearningMonitoring',
                                         [exp, 'false_discovery_recall_curve']);
  var picture = document.createElement('img');
  picture.setAttribute('class', 'img-responsive');
  picture.src = precision_recall_path;
  div.appendChild(picture);
}
