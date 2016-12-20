var project    = window.location.pathname.split('/')[2];
var dataset    = window.location.pathname.split('/')[3];
var experiment = window.location.pathname.split('/')[4];
var iteration  = window.location.pathname.split('/')[5];

var menu = $('#menu')[0];
var ul = document.createElement('ul');
menu.appendChild(ul);

var analyses       = ['topN', 'random', 'clustering'];
var analyses_names = ['Top N', 'Random', 'Clustering'];

for (i in analyses) {
    var analysis = analyses[i];
    var name     = analyses_names[i];
    var li = document.createElement('li');
    var elem = document.createElement('a');
    var text = document.createTextNode(name);
    elem.appendChild(text);
    if (analysis != 'clustering') {
      var query = buildQuery('alerts',
                      [project, dataset, experiment, iteration, analysis]);
    } else {
      var validation_project = project;
      var validation_dataset = getValidationDataset(project, dataset, 
                      experiment);
      var clustering_experiment_id = getAlertsClusteringExperimentId(
                      project, dataset, experiment);
      var query = buildQuery('SecuML',
                              [validation_project, validation_dataset,
                              clustering_experiment_id]);
    }
    elem.setAttribute('href', query);
    li.appendChild(elem);
    ul.appendChild(li);
}
