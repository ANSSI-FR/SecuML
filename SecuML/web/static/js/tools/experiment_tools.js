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

function datasetHasFamilies(experiment_id) {
    var query = buildQuery('datasetHasFamilies',
                           [experiment_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var families_monitoring = xmlHttp.responseText == 'True';
    return families_monitoring;
}

function getAlertsClusteringExperimentId(experiment_id) {
    var query = buildQuery('getAlertsClusteringExperimentId', [experiment_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var clustering_exp_id = xmlHttp.responseText;
    if (clustering_exp_id == 'None') {
        return null;
    } else {
        return clustering_exp_id;
    }
}

// Display the analysis of the selected feature
function getCoefficientsCallback(experiment_id) {
    var callback = function coefficientsCallback(active_bars) {
      var selected_index = active_bars[0]._index;
      var selected_feature = active_bars[0]._view.label;

      var query = buildQuery('getFeaturesAnalysisExp', [experiment_id]);
      var xmlHttp = new XMLHttpRequest();
      xmlHttp.open('GET', query, false);
      xmlHttp.send(null);
      var stats_exp_id = xmlHttp.responseText;
      if (stats_exp_id != 'None') {
        var page_query = buildQuery('SecuML', [stats_exp_id, selected_feature]);
        window.open(page_query);
      } else {
        var message = ['Features analysis is not available.',
                       'You must run SecuML_features_analysis.']
        displayAlert('no_stats', 'Warning', message);
      }
    }
    return callback;
}
