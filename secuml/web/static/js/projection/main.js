var path = window.location.pathname.split('/');
var exp_id = path[2];
var exp_type = 'Projection';

var tooltip = d3.select('body').append('div')
.attr('class', 'tooltip')
.style('opacity', 0);

var iteration = 0;
var label_method = 'projection';

var last_instance_selector = null;
var last_family = {'malicious': 'other', 'benign': 'other'};

var num_components_to_display = null;
var conf = {}

function callback() {
    num_components_to_display = getNumComponents();
    conf.projection_type = conf.core_conf.__type__.split('Conf')[0];
    generateDivisions(conf);
    displaySettings(conf);
    createInstancesSelectors();
    displayInstanceInformationStructure();
    displayAnnotationDiv();
    if (num_components_to_display > 10) {
        num_components_to_display = 10;
    }
    drawComponentsSelectors(num_components_to_display, printComponents);
    drawComponents(exp_id, 0, 1);
    if (conf.projection_type == 'Pca') {
      createProjectionErrorDiv();
      drawComponentsErrorEvolution(conf.projection_type, exp_id);
    }
    addShortcuts();
}

loadConfigurationFile(exp_id, callback);
