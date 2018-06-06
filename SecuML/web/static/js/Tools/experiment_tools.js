function createExperimentDiv(col_size, parent_div) {
  var experiment_panel = createCollapsingPanel('panel-info',
                                               col_size,
                                               'Experiment',
                                               parent_div,
                                               'settings');
  experiment_panel.setAttribute('style', 'font-size:smaller');
}

function getIterationSupervisedExperiment(conf, iteration) {
    var query = buildQuery('getIterationSupervisedExperiment',
            [conf.experiment_id, iteration]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var sup_exp = xmlHttp.responseText;
    return sup_exp;
}

function getTestExperimentId(experiment_id) {
    var query = buildQuery('getTestExperimentId',
                           [experiment_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var test_experiment_id = xmlHttp.responseText;
    return test_experiment_id;
}

function datasetHasFamilies(experiment_id) {
    var query = buildQuery('datasetHasFamilies',
                           [experiment_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var families_monitoring = xmlHttp.responseText == 'True';
    return families_monitoring;
}

// Display the descriptive statistics of the selected feature
function getCoefficientsCallback(experiment_id) {
    var callback = function coefficientsCallback(active_bars) {
      var selected_index = active_bars[0]._index;
      var selected_feature = active_bars[0]._view.label;
      var query = buildQuery('getDescriptiveStatsExp',
                             [experiment_id]);
      var xmlHttp = new XMLHttpRequest();
      xmlHttp.open('GET', query, false);
      xmlHttp.send(null);
      var stats_exp_id = xmlHttp.responseText;
      if (stats_exp_id != 'None') {
        var page_query = buildQuery('SecuML',
                [stats_exp_id, selected_feature]);
        window.open(page_query);
      } else {
        var message = ['Descriptive statistics are not available.',
                       'You must run SecuML_descriptive_stats.']
        displayAlert('no_stats', 'Warning', message);
      }
    }
    return callback;
}
