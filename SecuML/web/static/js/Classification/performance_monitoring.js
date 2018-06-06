function familiesMonitoring(conf, train_test) {
    if (! conf.classification_conf.probabilist_model) {
        return false;
    }
    if (conf.classification_conf.families_supervision) {
        return false;
    }
    if (train_test == 'validation') {
        var validation_exp_id = getTestExperimentId(conf.experiment_id);
        return datasetHasFamilies(validation_exp_id);
    } else {
        return datasetHasFamilies(conf.experiment_id);
    }
}

function displayPerformanceTabs(conf, train_test) {
    var performance_div_name =  train_test + '_performance';
    if (conf.classification_conf.families_supervision) {
      var menu_labels = [train_test + '_performance_indicators'];
      var menu_titles = ['Indicators'];
    } else {
      var menu_labels = [train_test + '_performance_indicators',
                         train_test + '_performance_roc',
                         train_test + '_performance_confusion_matrix'];
      var menu_titles = ['Indicators', 'ROC', 'Confusion Matrix'];
    }
    var families_monitoring = familiesMonitoring(conf, train_test);
    if (families_monitoring) {
      menu_titles.push('Families');
      menu_labels.push(train_test + '_families');
    }
    var menu = createTabsMenu(menu_labels, menu_titles,
            document.getElementById(performance_div_name),
            train_test + '_performance_monitoring_tabs');
    document.getElementById(performance_div_name).style.marginTop = '2px';
}

function updatePerformanceDisplay(conf, train_test, sup_exp, selected_fold) {
    var exp = conf.experiment_id;
    if (sup_exp) {
      exp = sup_exp;
    }
    // Indicators
    var indicators = cleanDiv(train_test + '_performance_indicators');
    displayPerfIndicators(indicators, conf, train_test, exp, selected_fold);
    if (! conf.classification_conf.families_supervision) {
      // ROC
      var roc = cleanDiv(train_test + '_performance_roc');
      displayROC(roc, conf, train_test, exp, selected_fold);
      // Confusion Matrix
      var confusion_matrix = cleanDiv(train_test + '_performance_confusion_matrix');
      displayConfusionMatrix(confusion_matrix, conf, train_test, exp, selected_fold);
    }
    var families_monitoring = familiesMonitoring(conf, train_test);
    if (families_monitoring) {
      displayFamiliesMonitoring(conf, train_test, sup_exp);
    }
}

function sliderCallback(conf, train_test, sup_exp, event, ui) {
  return function(event, ui) {
    var threshold_col = cleanDiv('threshold_col_' + train_test);
    var value = $('#slider_' + train_test).slider('value');
    threshold_col.appendChild(document.createTextNode('Detection threshold: ' + value + '%'));
    var performance_path = buildQuery('supervisedLearningMonitoring',
                                      [sup_exp, train_test, 'perf_indicators', 'None']);
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

function displayPerfIndicators(div_obj, conf, train_test, exp, selected_fold) {
  if (conf.classification_conf.probabilist_model && !conf.classification_conf.families_supervision) {
      displayThresholdPerfIndicators(div_obj, conf, train_test, exp, selected_fold);
  } else {
      displayNoThresholdPerfIndicators(div_obj, conf, train_test, exp, selected_fold);
  }
}

function displayNoThresholdPerfIndicators(div_obj, conf, train_test, exp, selected_fold) {
  var train_performance_path = buildQuery('supervisedLearningMonitoring',
                                          [exp, train_test, 'perf_indicators',
                                          selected_fold]);
  var header = null;
  if (train_test == 'cv') {
      header = ['Indicator', 'Mean', 'Std'];
  }
  var body = createTable(div_obj.id, header,
          table_id = 'perf_ind_table_' + train_test);
  $.getJSON(train_performance_path,
            function(data) {
                if (conf.classification_conf.families_supervision) {
                  var fields_names = ['f1_micro', 'f1_macro', 'accuracy'];
                  var fields_names_display = ['F1-micro', 'F1-macro', 'Accuracy'];
                } else {
                  var fields_names = ['recall', 'false_positive', 'f-score', 'auc'];
                  var fields_names_display = ['Detection', 'False alarms', 'F-score', 'AUC'];
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
                    addRow(body, elements, title = true);
                }
            }
           );
}

function displayThresholdPerfIndicators(div_obj, conf, train_test, exp, selected_fold) {
  var train_performance_path = buildQuery('supervisedLearningMonitoring',
                                          [exp, train_test, 'perf_indicators',
                                           selected_fold]);
  // Slider to select the detection threshold
  var slider_row = createDivWithClass('slider_row_' + train_test, 'row', parent_div = div_obj);
  var threshold_col = createDivWithClass('threshold_col_' + train_test, 'col-md-6', parent_div = slider_row);
  threshold_col.appendChild(document.createTextNode('Detection threshold: 50%'));
  var slider_col = createDivWithClass('slider_col_' + train_test, 'col-md-6', parent_div = slider_row);
  createDiv('slider_' + train_test, parent_div = slider_col);
  $( function() {
    $('#slider_' + train_test).slider({
        min:0,
        max: 100,
        value: 50,
        range: 'max',
        change: sliderCallback(conf, train_test, exp)
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
                  fields_names = ['recall', 'false_positive', 'f-score'];
                  fields_names_display = ['Detection', 'False alarms', 'F-score'];
                } else {
                  fields_names = ['recall', 'false_positive', 'f-score', 'auc'];
                  fields_names_display = ['Detection', 'False alarms', 'F-score', 'AUC'];
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

function displayConfusionMatrix(div_obj, conf, train_test, exp, selected_fold) {
    var benign_label = 'ok';
    var malicious_label = 'alert';
    var confusion_matrix_path = buildQuery('supervisedLearningMonitoring',
                                           [exp, train_test, 'confusion_matrix',
                                            selected_fold]);
    var table = createTable(div_obj.id, null,
                    ['', '', malicious_label, benign_label],
                    table_id = null);
    $.getJSON(confusion_matrix_path,
              function(data) {

                var errors_query = buildQuery('errors',
                        [exp, train_test, selected_fold]);

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
                if (selected_fold != 'all') {
                  var fn_elem = document.createElement('a');
                  var fn_text = document.createTextNode(data['FN']);
                  fn_elem.appendChild(fn_text);
                  fn_elem.href = errors_query;
                  fn_elem.setAttribute('title', 'Not Detected');
                } else {
                  var fn_elem = document.createTextNode(data['FN']);
                }
                cell.appendChild(fn_elem);
                cell.id = 'FN';

                var row = table.insertRow(3);
                var cell = row.insertCell(0);
                cell.innerHTML = benign_label;
                var cell = row.insertCell(1);
                if (selected_fold != 'all') {
                  var fp_elem = document.createElement('a');
                  var fp_text = document.createTextNode(data['FP']);
                  fp_elem.appendChild(fp_text);
                  fp_elem.href = errors_query;
                  fp_elem.setAttribute('title', 'False Positives');
                } else {
                  var fp_elem = document.createTextNode(data['FP']);
                }
                cell.appendChild(fp_elem);
                cell.id = 'FP';
                var cell = row.insertCell(2);
                cell.innerHTML = data['TN'];
    });
}

function displayROC(div, conf, train_test, exp, selected_fold) {
  var ROC_path = buildQuery('supervisedLearningMonitoring',
                            [exp, train_test, 'ROC',
                             selected_fold]);
  var picture = document.createElement('img');
  picture.setAttribute('class', 'img-responsive');
  picture.src = ROC_path;
  div.appendChild(picture);
}
