function generateDivisions(conf) {
  generateTitle('DIADEM - ' + classifier_conf.model_class_name);

  // Experiment
  var experiment = createExperimentDiv(null, $('#exp')[0]);

  // Monitoring row
  var test_method = test_conf.method
  if (['cv', 'temporal_cv', 'sliding_window'].indexOf(test_method) > -1) {
    displayFoldIdSelectList(conf, $('#select_fold')[0]);
    displayMonitoringRow(conf, 'all');
  } else {
    displayMonitoringRow(conf);
  }
}

function displayFoldIdMonitoring(conf) {
    return function() {
        var fold_id_select = document.getElementById('fold_id_select')
        var selected_fold = getSelectedOption(fold_id_select);
        displayMonitoringRow(conf, selected_fold);
    }
}

function displayFoldIdSelectList(conf, div) {
  var num_folds = test_conf.num_folds;
  var select_fold_div = createDivWithClass(null, 'col-md-6', div);
  var fold_id_select = createSelectList('fold_id_select', 1,
                                        displayFoldIdMonitoring(conf),
                                        select_fold_div, 'Select a fold');
  var elem_list = [];
  var test_method = test_conf.method
  if (['cv', 'temporal_cv', 'sliding_window'].indexOf(test_method) > -1) {
      elem_list.push('all');
  }
  for (var i = 0; i < num_folds; i++) {
      elem_list.push(i);
  }
  addElementsToSelectList('fold_id_select', elem_list);
}

function displayMonitoringRow(conf, selected_fold) {
  if (!selected_fold) {
    selected_fold = 'None';
  }

  if (selected_fold == 'all') {
    displayChildMonitoring(conf, 'cv', 'None');
  } else {
    displayChildMonitoring(conf, 'train', selected_fold);
    displayChildMonitoring(conf, 'test', selected_fold);
  }
}
