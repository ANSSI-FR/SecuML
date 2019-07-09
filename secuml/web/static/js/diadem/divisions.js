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


function displayFoldIdSelectList(conf, div) {
  function displayFoldIdMonitoring(conf) {
      return function() {
          var fold_id_select = document.getElementById('fold_id_select')
          var selected_fold = getSelectedOption(fold_id_select);
          displayMonitoringRow(conf, selected_fold);
      }
  }
  var num_folds = test_conf.num_folds;
  var select_fold_div = createDivWithClass(null, 'col-md-6', div);
  var fold_id_select = createSelectList('fold_id_select', 1,
                                        displayFoldIdMonitoring(conf),
                                        select_fold_div, 'Select a fold');
  var elem_list = ['all'];
  for (var i = 0; i < num_folds; i++) {
      elem_list.push(i);
  }
  addElementsToSelectList('fold_id_select', elem_list);
}

function displayTestDatasetsSelectList(conf, div) {
  function displayDatasetMonitoring(conf) {
      return function() {
          var dataset_select = document.getElementById('dataset_select')
          var selected_dataset = getSelectedOption(dataset_select);
          displayDetectionMonitoring(conf, 'test', 'None',
                                     selected_dataset);
      }
  }
  var select_div = createDivWithClass(null, 'col-md-6', div);
  var dataset_select = createSelectList('dataset_select', 1,
                                        displayDatasetMonitoring(conf),
                                        select_div,
                                        'Select a test dataset');
  var elem_list = ['all'];
  elem_list = elem_list.concat(test_conf.validation_datasets);
  addElementsToSelectList('dataset_select', elem_list);
}

function displayMonitoringRow(conf, selected_fold) {
  if (!selected_fold) {
    selected_fold = 'None';
  }
  if (selected_fold == 'all') {
    displayDetectionMonitoring(conf, 'cv', 'None');
    displayTrainingMonitoring(conf, 'None', 'cv');
    cleanDiv('test');
  } else {
    if (!conf.no_training_detection) {
        displayDetectionMonitoring(conf, 'train', selected_fold);
    }
    if (test_conf.method == 'datasets' &&
            test_conf.validation_datasets.length > 1) {
        displayTestDatasetsSelectList(conf, $('#select_dataset')[0]);
        displayDetectionMonitoring(conf, 'test', selected_fold, 'all');
    } else {
        displayDetectionMonitoring(conf, 'test', selected_fold);
    }
    displayTrainingMonitoring(conf, selected_fold, 'train');
  }
}
