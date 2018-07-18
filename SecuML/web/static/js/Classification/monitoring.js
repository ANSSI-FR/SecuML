var num_coeff_model = 15;

function createTrainTestMonitoring(train_test, col_size, parent_div) {
    var panel_title = upperCaseFirst(train_test)
        if (panel_title == 'Cv') {
            panel_title = 'Cross Validation';
        }
    var monitoring = createPanel('panel-primary', col_size, panel_title, parent_div);
    createDivWithClass(train_test + '_monitoring', 'tabbable boxed parentTabs', monitoring);
}

function displayAlertsButton(buttons_group, button_label, buttons_title, selected_fold) {
    var label_group = createDivWithClass(null, 'btn-group', parent_div = buttons_group);
    var label_button = document.createElement('button');
    label_button.setAttribute('class', 'btn btn-danger');
    label_button.setAttribute('type', 'button');
    label_button.setAttribute('id', button_label + '_button');
    var label_button_text = document.createTextNode(buttons_title);
    label_button.appendChild(label_button_text);
    label_button.addEventListener('click', function() {
        if (button_label != 'clustering') {
            var query = buildQuery('alerts',
                    [experiment_id, button_label, selected_fold]);
            window.open(query);
        } else {
            var query = buildQuery('getAlertsClusteringExperimentId',
                    [experiment_id, selected_fold]);
            d3.json(query, function(error, data) {
                var clustering_experiment_id = data['grouping_exp_id'];
                if (! clustering_experiment_id) {
                    message = ['There is no clustering of the alerts.'];
                    displayAlert('no_alert_clustering', 'Warning', message);
                } else {
                    var query = buildQuery('SecuML',
                            [clustering_experiment_id]);
                    window.open(query);
                }
            });
        }
    });
    label_group.appendChild(label_button);
}

function displayAlertsButtons(selected_fold) {
    var test_monitoring = document.getElementById('test_monitoring');
    var alerts_div = createPanel('panel-danger', null, 'Alerts Analysis', test_monitoring);
    var buttons_group = createDivWithClass(null, 'btn-group btn-group-justified', parent_div = alerts_div);
    var labels = ['topN', 'random', 'clustering'];
    var titles = ['Top N', 'Random', 'Clustering'];
    for (var i = 0; i < labels.length; i++) {
        displayAlertsButton(buttons_group, labels[i], titles[i], selected_fold);
    }
}

function displayMonitoring(conf, train_test, selected_fold) {
    if (checkDisplayCoefficients(train_test, exp_type, conf)) {
        displayCoefficients(conf, null, train_test, selected_fold);
    }
    displayMonitoringTabs(conf, train_test);
    updateMonitoringDisplay(conf, train_test, null, selected_fold);
}

function updateMonitoringDisplay(conf, train_test, sup_exp = null, selected_fold = null) {
    if (checkDisplayPredictions(conf)) {
      updatePredictionsDisplay(conf, train_test, sup_exp, selected_fold);
    }
    if (checkDisplayPerformance(train_test, conf, exp_type)) {
        updatePerformanceDisplay(conf, train_test, sup_exp, selected_fold);
    }
}

function displayMonitoringTabs(conf, train_test) {
    var tabs_div = document.getElementById(train_test + '_monitoring');;
    var menu_titles = [];
    var menu_labels = [];
    if (checkDisplayPerformance(train_test, conf, exp_type)) {
        var menu_titles = ['Performance'];
        var menu_labels = [train_test + '_performance'];
    }
    if (checkDisplayPredictions(conf)) {
        menu_titles.push('Predictions');
        menu_labels.push(train_test + '_predictions');
    }
    var menu = createTabsMenu(menu_labels, menu_titles,
            tabs_div, train_test + '_monitoring_tabs');
    if (checkDisplayPerformance(train_test, conf, exp_type)) {
        displayPerformanceTabs(conf, train_test);
    }
}

function displayCoefficients(conf, sup_exp, train_test, selected_fold) {
        var exp = conf.experiment_id;
        if (sup_exp) {
            exp = sup_exp;
        }
        var model_coefficients_div = cleanDiv('model_coefficients');
        var query = buildQuery('getTopModelFeatures',
                [exp, num_coeff_model,
                train_test, selected_fold]);
        $.getJSON(query, function (data) {
            var options = barPlotOptions(data);
            barPlotAddTooltips(options, data.tooltip_data);
            barPlotAddBands(options, true);
            options.legend.display = false;
            var barPlot = drawBarPlot('model_coefficients',
                    options,
                    data,
                    type = 'horizontalBar',
                    width = null,
                    height = '400px',
                    callback = getCoefficientsCallback(conf.experiment_id));
        });
}

function checkDisplayCoefficients(train_test, exp_type, conf) {
    if (train_test == 'train' || train_test == 'cv') {
        if (exp_type == 'Classification' || exp_type == 'ActiveLearning') {
            var multilabel = conf.classification_conf.families_supervision;
            if (!multilabel) {
                if (conf.classification_conf.feature_importance) {
                    return true;
                }
            }
        }
    }
    return false;
}

function checkDisplayPredictions(conf) {
    var multilabel        = conf.classification_conf.families_supervision;
    var probabilist_model = conf.classification_conf.probabilist_model;
    return probabilist_model && !multilabel;
}

function checkDisplayPerformance(train_test, conf, exp_type) {
    var no_ground_truth = validationWithoutGroundTruth(train_test, conf,
            exp_type);
    return !no_ground_truth;
}

function validationWithoutGroundTruth(train_test, conf, exp_type) {
    if (exp_type == 'Classification') {
        return train_test == 'test' && !conf.validation_has_ground_truth;
    } else if (exp_type == 'ActiveLearning') {
        var res = train_test == 'test' && !conf.has_ground_truth;
        res = res || (train_test == 'validation' & !conf.validation_has_ground_truth);
        return res;
    }
}

function checkDisplayAlerts(conf) {
  if (conf.classification_conf.test_conf.alerts_conf) {
      var multilabel = conf.classification_conf.families_supervision;
      if (!multilabel) {
          return true;
      }
  }
  return false;
}
