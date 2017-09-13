function createExperimentDiv(col_size, parent_div) {
  var experiment_panel = createCollapsingPanel('panel-info', col_size, 'Experiment', parent_div,
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

function getValidationDataset(experiment_id) {
    var query = buildQuery('getValidationDataset',
                           [experiment_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var validation_dataset = xmlHttp.responseText;
    return validation_dataset;
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

function getTrueLabelsExperiment(experiment_id) {
    var query = buildQuery('getTrueLabelsExperiment',
                           [experiment_id]);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', query, false);
    xmlHttp.send(null);
    var true_label_exp_id = xmlHttp.responseText;
    return true_label_exp_id;
}
