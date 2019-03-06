function loadConfigurationFile(exp_id, callback) {
  d3.json(buildQuery('getConf', [exp_id]),
          function(data) {
            conf = data;
            annotations_id = conf.annotations_conf.annotations_id;
            annotations_type = conf.annotations_conf.annotations_type;
            dataset_id = conf.dataset_conf.dataset_id;
            callback(conf);
  });
}

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
            [conf.exp_id, iteration]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var sup_exp = xmlHttp.responseText;
    return sup_exp;
}

function getAlertsClusteringExpId(diadem_exp_id) {
    var query = buildQuery('getAlertsClusteringExpId', [diadem_exp_id]);
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

function hasGroundTruth(project, dataset){
    var query = buildQuery('hasGroundTruth', [project, dataset]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var has_ground_truth = xmlHttp.responseText == 'True';
    return has_ground_truth;
}

// Display the analysis of the selected feature
function getCoefficientsCallback(exp_id) {
    var callback = function coefficientsCallback(active_bars) {
      var selected_index = active_bars[0]._index;
      var selected_feature = active_bars[0]._view.label;
      var query = buildQuery('getFeaturesAnalysisExp', [exp_id]);
      var xmlHttp = new XMLHttpRequest();
      xmlHttp.open('GET', query, false);
      xmlHttp.send(null);
      var stats_exp_id = xmlHttp.responseText;
      if (stats_exp_id != 'None') {
        var page_query = buildQuery('SecuML', ['featuresExp', stats_exp_id,
                                               selected_feature]);
        window.open(page_query);
      } else {
        var message = ['Features analysis is not available.',
                       'You must run SecuML_features_analysis.']
        displayAlert('no_stats', 'Warning', message);
      }
    }
    return callback;
}
