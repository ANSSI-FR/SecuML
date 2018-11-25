var path          = window.location.pathname.split('/');
var experiment_id = path[2];
var exp_type      = 'FeatureSelection';

var tooltip = d3.select('body').append('div')
.attr('class', 'tooltip')
.style('opacity', 0);

var label_iteration = 0;
var label_method = 'feature_selection';

var has_families = datasetHasFamilies(experiment_id);
var inst_exp_id = experiment_id;

var last_instance_selector = null;
var last_family = {'malicious': 'other', 'benign': 'other'};

var num_components_to_display = null;
var conf = {}
loadConfigurationFile(onceConfigurationIsLoaded('feature selection'));
addShortcuts();
