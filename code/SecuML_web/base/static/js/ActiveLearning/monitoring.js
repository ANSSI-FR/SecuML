function displayEvolutionMonitoringRadioButtons(args, conf) {
  var div_name = 'evolution_monitoring';
  var div_obj = cleanDiv(div_name);
  var radio_name = 'radio_monitoring';
  var radio_div = createDivWithClass(radio_name, 'row',
          parent_div = div_obj);
  var sub_monitoring = createDivWithClass('sub_monitoring', 'row',
          parent_div = div_obj);
  var radio_sublabels = makeRadioButton(radio_name,
          'sublabels', 'Sublabels', 
          true, function() {
              var AL_monitoring_graph_div = createDiv('AL_monitoring_graph',
                      parent_div = sub_monitoring);
              displayActiveLearningMonitoring(args, conf);
          },
          parent_div = radio_div);
  if (conf.labeling_method == 'ILAB' && conf.has_true_labels) {
      var radio_clustering = makeRadioButton(radio_name,
              'clustering', 'Clustering',
              false, function() {
                displayClusteringEvalRadioButton(args, conf, 'sub_monitoring');
              },
              parent_div = radio_div);
  }
  if (conf.validation_conf) {
      var radio_validation = makeRadioButton(radio_name,
              'validation', 'Validation', 
              false, function() {
                displayActiveLearningValidationMonitoringRadioButton(
                                args, conf, 'sub_monitoring');
              },
              parent_div = radio_div);
  }
  var radio_time = makeRadioButton(radio_name,
          'time', 'time', 
          false, function() {
              var AL_monitoring_graph_div = createDiv('AL_monitoring_graph',
                      parent_div = sub_monitoring);
              displayActiveLearningMonitoring(args, conf);
          },
          parent_div = radio_div);
  displayActiveLearningMonitoring(args, conf);
}

function displayActiveLearningMonitoring(args, conf) {
    var iteration = getIteration();
    if (!iteration) {
        // No iteration selected
        return;
    }
    var radio_sublabels = $('#radio_sublabels')[0];
    var radio_clustering = $('#radio_clustering')[0];
    var radio_validation = $('#radio_validation')[0];
    var radio_time = $('#radio_time')[0];
    //var radio_labels = $('#radio_labels');
    //if (radio_labels.checked) {
    //    displayActiveLearningLabelMonitoring(args, iteration);
    if (radio_sublabels.checked) {
        displayActiveLearningSublabelsMonitoring(args, iteration);
    } else if (conf.labeling_method == 'ILAB' && conf.has_true_labels && radio_clustering.checked) {
        displayClusteringEvalMonitoring(args, iteration);
    } else if (conf.validation_conf && radio_validation.checked) { 
        displayActiveLearningValidationMonitoring(args, iteration);
    } else if (radio_time.checked) {
        displayExecutionTimeMonitoring(args, iteration);
    }
} 

function displayClusteringEvalRadioButton(args, conf, div_name) {
  var div = cleanDiv(div_name);
  var radio_name = 'radio_sub_monitoring';
  var radio_div = createDiv(radio_name, 
          parent_div = div);
  var AL_monitoring_graph_div = createDiv('AL_monitoring_graph',
          parent_div = div);
  var radio_vmeasure = makeRadioButton(radio_name,
          'vmeasure', 'V measure', 
          false, function() {
            displayActiveLearningMonitoring(args, conf);
          },
          parent_div = radio_div);
  var radio_homogeneity = makeRadioButton(radio_name,
          'homogeneity', 'Homogeneity', 
          true, function() {
            displayActiveLearningMonitoring(args, conf);
          },
          parent_div = radio_div);
  var radio_completeness = makeRadioButton(radio_name,
          'completeness', 'Completeness', 
          false, function() {
            displayActiveLearningMonitoring(args, conf);
          },
          parent_div = radio_div);
  displayActiveLearningMonitoring(args, conf);
}

function displayActiveLearningLabelMonitoringRadioButton(args, conf, div_name) {
  var div = cleanDiv(div_name);
  var radio_name = 'radio_sub_monitoring';
  var radio_div = createDiv(radio_name, 
          parent_div = div);
  var AL_monitoring_graph_div = createDiv('AL_monitoring_graph',
          parent_div = div);
  var radio_global = makeRadioButton(radio_name,
          'global', 'Global', 
          true, function() {
            displayActiveLearningMonitoring(args, conf);
          },
          parent_div = radio_div);
  var radio_malicious = makeRadioButton(radio_name,
          'malicious', 'Malicious', 
          false, function() {
            displayActiveLearningMonitoring(args, conf);
          },
          parent_div = radio_div);
  var radio_benign = makeRadioButton(radio_name,
          'benign', 'Benign', 
          false, function() {
            displayActiveLearningMonitoring(args, conf);
          },
          parent_div = radio_div);
  displayActiveLearningMonitoring(args, conf);
}

function displayClusteringEvalMonitoring(args, iteration) {
    var radio_homogeneity = $('#radio_homogeneity')[0];
    var radio_completeness = $('#radio_completeness')[0];
    var estimator = 'v_measure';
    if (radio_homogeneity.checked) {
        estimator = 'homogeneity';
    } else if (radio_completeness.checked) {
        estimator = 'completeness';
    }
    div = cleanDiv('AL_monitoring_graph');
    var query = buildQuery('activeLearningMonitoring',
        args.concat([iteration, 'clustering', estimator]));
    var picture = document.createElement('img');
    picture.src = query;
    picture.style.width = '80%';
    picture.style.height = 'auto';
    div.appendChild(picture); 
}

function displayActiveLearningLabelMonitoring(args, iteration) {
    var radio_global = $('#radio_global')[0];
    var radio_malicious = $('#radio_malicious')[0];
    if (radio_global.checked) {
        var label = 'global';
    } else if (radio_malicious.checked) {
        var label = 'malicious';
    } else {
        var label = 'benign';
    }
    div = cleanDiv('AL_monitoring_graph');
    var query = buildQuery('activeLearningMonitoring',
        args.concat([iteration, 'labels', label]));
    var picture = document.createElement('img');
    picture.src = query;
    picture.style.width = '80%';
    picture.style.height = 'auto';
    div.appendChild(picture); 
}

function displayExecutionTimeMonitoring(args, iteration) {
    var sub_monitoring = cleanDiv('sub_monitoring');
    var AL_monitoring_graph_div = createDiv('AL_monitoring_graph',
            parent_div = sub_monitoring);
    var query = buildQuery('activeLearningMonitoring',
        args.concat([iteration, 'time', 'all']));
    var picture = document.createElement('img');
    picture.src = query;
    picture.style.width = '80%';
    picture.style.height = 'auto';
    AL_monitoring_graph_div.appendChild(picture); 
}

function displayActiveLearningSublabelsMonitoring(args, iteration) {
    var sub_monitoring = cleanDiv('sub_monitoring');
    var AL_monitoring_graph_div = createDiv('AL_monitoring_graph',
            parent_div = sub_monitoring);
    var query = buildQuery('activeLearningMonitoring',
        args.concat([iteration, 'sublabels', 'all']));
    var picture = document.createElement('img');
    picture.src = query;
    picture.style.width = '80%';
    picture.style.height = 'auto';
    AL_monitoring_graph_div.appendChild(picture); 
}

function displayActiveLearningValidationMonitoringRadioButton(args, conf, div_name) {
    div = cleanDiv(div_name);
    var radio_name = 'radio_sub_monitoring';
    var radio_div = createDiv(radio_name,
            parent_div = div);
    var AL_monitoring_graph_div = createDiv('AL_monitoring_graph',
            parent_div = div);
    var radio_auc = makeRadioButton(radio_name,
            'auc', 'AUC', 
            true, function() {
              displayActiveLearningMonitoring(args, conf);
            },
            parent_div = radio_div);
    var radio_fscore = makeRadioButton(radio_name,
            'fscore', 'F-score', 
            false, function() {
              displayActiveLearningMonitoring(args, conf);
            },
            parent_div = radio_div);
    displayActiveLearningMonitoring(args, conf);
}

function displayActiveLearningValidationMonitoring(args, iteration) {
    var estimator = 'auc';
    var radio_fscore = $('#radio_fscore')[0];
    if (radio_fscore.checked) {
        estimator = 'fscore';
    }
    div = cleanDiv('AL_monitoring_graph');
    var query = buildQuery('activeLearningMonitoring',
        args.concat([iteration, 'validation', estimator]));
    var picture = document.createElement('img');
    picture.src = query;
    picture.style.width = '80%';
    picture.style.height = 'auto';
    div.appendChild(picture); 
}
