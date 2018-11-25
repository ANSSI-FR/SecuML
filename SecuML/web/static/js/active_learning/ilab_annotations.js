var path = window.location.pathname.split('/');
var experiment_id     = path[2];
var label_iteration   = path[3];
var exp_type          = 'ActiveLearning';

var annotations_types = null;
var label_method      = null;

var current_label        = null;
var families_list        = null;
var num_families         = null;
var current_family_index = null;

var instances_list         = null;
var confidence_list        = null;
var num_instances          = null;
var current_instance_index = null;

var inst_exp_id = experiment_id;
var inst_annotations_id = null;
var has_families = datasetHasFamilies(inst_exp_id);

var conf = {};
loadConfigurationFile(callback);
addShortcuts();

var annotation_queries = null;

function callback() {
    displayButtons();
    displayAnnotationDivision(true);
    displayInstancesToAnnotate('uncertain', 'warning')();
}

function loadConfigurationFile(callback) {
    d3.json(buildQuery('getConf', [experiment_id]),
            function(error, data) {
                conf = data;
                conf.interactive = false;
                setInstancesSettings('train', experiment_id);
                if (!conf.core_conf.auto) {
                    var current_iteration = currentAnnotationIteration(experiment_id);
                    conf.interactive = label_iteration == current_iteration;
                }

                d3.json(buildQuery('getAnnotationsTypes', [experiment_id, label_iteration]),
                        function(error, data) {
                            annotations_types = data;
                            callback();
                        }
                       );
            });
}

function displayInstancesToAnnotate(label, type) {
    return function () {
        current_label = label;
        current_type  = type;
        label_method  = 'annotation_' + label;
        var annotations_type = annotations_types[label]['type'];
        var clustering_exp = annotations_types[label]['clustering_exp'];
        displayNavbars(type, annotations_type, clustering_exp);
        if (annotations_type == 'families') {
            var query = buildQuery('getFamiliesInstancesToAnnotate',
                                   [experiment_id, label_iteration, label]);
            d3.json(query, function(error, data) {
                annotation_queries = data;
                families_list = Object.keys(data);
                // The families with no annotation query are not displayed.
                families_list = families_list.filter(
                        function nonEmpty(x) {
                            return annotation_queries[x]['instance_ids'].length > 0;
                        });
                num_families = families_list.length;
                current_family_index = 0;
                updateFamilyNavbar();
            });
        } else if (annotations_type == 'individual') {
            var query = buildQuery('getInstancesToAnnotate',
                                   [experiment_id, label_iteration, label]);
            d3.json(query, function(error, data) {
                instances_list = data['instances'];
                families_list = null;
                num_families = null;
                current_family_index = null;
                confidence_list = null;
                num_instances = instances_list.length;
                current_instance_index = 0;
                updateInstanceNavbar();
            });
        }
    }
}

function displayFamilyInstancesToAnnotate(family) {
    instances_list  = annotation_queries[family]['instance_ids'];
    confidence_list = annotation_queries[family]['confidence'];
    num_instances = instances_list.length;
    current_instance_index = 0;
    updateInstanceNavbar();
}

function displayNextInstance() {
    if (current_instance_index <= num_instances-2) {
        current_instance_index += 1;
        updateInstanceNavbar();
    }
}

function displayPrevInstance() {
    if (current_instance_index > 0) {
        current_instance_index -= 1;
        updateInstanceNavbar();
    } else {
        displayPrevFamily();
    }
}

function displayNextFamily() {
    if (current_family_index <= num_families-2) {
        current_family_index += 1;
        updateFamilyNavbar();
    }
}

function displayPrevFamily() {
    if (current_family_index > 0) {
        current_family_index -= 1;
        updateFamilyNavbar();
    }
}

function displayNextInstanceToAnnotate() {
    displayNextInstance();
}

function updateFamilyNavbar() {
    var iter_family = cleanDiv('iter_family');
    iter_family.appendChild(document.createTextNode((current_family_index+1) + ' / ' + num_families));
    var current_family = cleanDiv('current_family');
    current_family.appendChild(document.createTextNode(families_list[current_family_index]));
    displayFamilyInstancesToAnnotate(families_list[current_family_index]);
}

function updateInstanceNavbar() {
    var iter_label = cleanDiv('iter_label');
    iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
    var suggested_family = null;
    var suggested_label  = null;
    if (confidence_list) {
        if (confidence_list[current_instance_index] == 'high') {
            suggested_label  = current_label;
            suggested_family = families_list[current_family_index];
        }
    }
    printInstanceInformation(instances_list[current_instance_index],
                             suggested_label, suggested_family);
}

function updateAnnotationTypesButtons() {
    d3.json(buildQuery('getAnnotationsTypes', [experiment_id, label_iteration]),
            function(error, data) {
                annotations_types = data;
            });
    var labels = ['malicious', 'benign'];
    var types = ['danger', 'success'];
    for (var i in labels) {
        var label = labels[i];
        var type = types[i];
        var button = document.getElementById(label + '_button');
        if (annotations_types[label]) {
            button.setAttribute('class', 'btn btn-lg btn-' + type);
            button.addEventListener('click', displayInstancesToAnnotate(label,
                                                                        type));
        }
    }
}

function displayButton(buttons_line, l, type, disabled) {
    var label_group = document.createElement('h3');
    label_group.setAttribute('class', 'col-md-1');
    buttons_line.appendChild(label_group);
    var label_button = document.createElement('button');
    var button_class = 'btn btn-lg btn-' + type;
    if (disabled) {
        button_class += ' disabled';
    }
    label_button.setAttribute('class', button_class);
    label_button.setAttribute('type', 'button');
    label_button.setAttribute('id', l + '_button');
    var label_button_text = document.createTextNode(upperCaseFirst(l));
    label_button.appendChild(label_button_text);
    if (!disabled) {
        label_button.addEventListener('click', displayInstancesToAnnotate(l,
                                                                          type));
    }
    label_group.appendChild(label_button);
}

function displayChevron(buttons_line) {
    var chevron_div = document.createElement('h1');
    chevron_div.setAttribute('class', 'col-md-1');
    chevron_div.appendChild(document.createTextNode('\u27a4'));
    chevron_div.appendChild(document.createTextNode('\u27a4'));
    chevron_div.appendChild(document.createTextNode('\u27a4'));
    buttons_line.appendChild(chevron_div);
}

function displayButtons() {
    var main = $('#main')[0];
    var buttons_line = createDivWithClass(null, 'form-group',
                                          parent_div=main);
    displayButton(buttons_line, 'uncertain', 'warning', false);
    displayChevron(buttons_line)
        displayButton(buttons_line, 'malicious', 'danger', true);
    displayChevron(buttons_line)
        displayButton(buttons_line, 'benign', 'success', true);

    window.setInterval(updateAnnotationTypesButtons, 10 * 1000);

    // End annotation process
    if (conf.interactive) {
        var end_group = document.createElement('h3');
        end_group.setAttribute('class', 'col-md-1 col-md-offset-2');
        buttons_line.appendChild(end_group);
        var end_button = document.createElement('button');
        end_button.setAttribute('class', 'btn btn-lg btn-primary');
        end_button.setAttribute('type', 'button');
        end_button.setAttribute('id', 'end_button');
        var end_button_text = document.createTextNode('Next Iteration');
        end_button.appendChild(end_button_text);
        end_button.addEventListener('click', runNextIteration(conf));
        end_group.appendChild(end_button);
    }
    var nav_bars = createDivWithClass('nav_bars', 'col-md-12', parent_div=main);
}

function displayNavbars(type, annotations_type, clustering_exp) {
    var nav_bars = cleanDiv('nav_bars');
    var panel_body = createPanel('panel-' + type, 'row',
            'Annotation Queries',
            nav_bars);
    var col = createDivWithClass(null, 'col-md-10', panel_body);
    if (annotations_type == 'families') {
        displayFamiliesBar(col, type);
    }
    displayAnnotationQueriesBar(col, type);
    if (annotations_type == 'families') {
        var col = createDivWithClass(null, 'col-md-2', panel_body);
        clusteringVisualization(col, clustering_exp);
    }
}

function clusteringVisualization(row, clustering_exp) {
    function displayClustering(clustering_exp) {
        return function() {
            var query = buildQuery('SecuML', [clustering_exp]);
            window.open(query);
        }
    }
    var group = createDivWithClass('', 'row', row);
    var button = document.createElement('button');
    button.setAttribute('class', 'btn btn-default');
    button.setAttribute('type', 'button');
    button.setAttribute('id', 'button_clustering');
    var button_text = document.createTextNode('Display Families');
    button.appendChild(button_text);
    button.addEventListener('click', displayClustering(clustering_exp));
    group.appendChild(button);
}

function displayFamiliesBar(panel_body, type) {
    var row = createDivWithClass(null, 'row form-group', parent_div=panel_body);

    var family_label = document.createElement('label');
    family_label.setAttribute('class', 'col-md-1 control-label');
    family_label.appendChild(document.createTextNode('Family'));
    row.appendChild(family_label);

    var current_family = createDivWithClass(null, 'col-md-2 control-label',
                                            parent_div=row);
    current_family.setAttribute('id', 'current_family');

    var iter_family = document.createElement('label');
    iter_family.setAttribute('class', 'col-md-1 control-label');
    iter_family.setAttribute('id', 'iter_family');
    row.appendChild(iter_family);

    // Prev / Next buttons
    var prev_next_group = createDivWithClass(null, 'col-md-2', row);
    // Prev button
    var prev_button = document.createElement('button');
    prev_button.setAttribute('class', 'btn btn-' + type);
    prev_button.setAttribute('type', 'button');
    prev_button.setAttribute('id', 'prev_button_family');
    var prev_button_text = document.createTextNode('Prev');
    prev_button.appendChild(prev_button_text);
    prev_button.addEventListener('click', displayPrevFamily);
    prev_next_group.appendChild(prev_button);
    // Next button
    var next_button = document.createElement('button');
    next_button.setAttribute('class', 'btn btn-' + type);
    next_button.setAttribute('type', 'button');
    next_button.setAttribute('id', 'next_button_family');
    var next_button_text = document.createTextNode('Next');
    next_button.appendChild(next_button_text);
    next_button.addEventListener('click', displayNextFamily);
    prev_next_group.appendChild(next_button);
}

function displayAnnotationQueriesBar(panel_body, type) {
    var row = createDivWithClass(null,  'row', parent_div=panel_body);
    var annotation_query_label = document.createElement('label');
    annotation_query_label.setAttribute('class', 'col-md-3 control-label');
    annotation_query_label.appendChild(document.createTextNode('Annotation Query'));
    row.appendChild(annotation_query_label);
    var iter_label = document.createElement('label');
    iter_label.setAttribute('class', 'col-md-1 control-label');
    iter_label.setAttribute('id', 'iter_label');
    row.appendChild(iter_label);
    // Prev / Next buttons
    var prev_next_group = createDivWithClass(null, 'col-md-3', row);
    // Prev button
    var prev_button = document.createElement('button');
    prev_button.setAttribute('class', 'btn btn-' + type);
    prev_button.setAttribute('type', 'button');
    prev_button.setAttribute('id', 'prev_button');
    var prev_button_text = document.createTextNode('Prev');
    prev_button.appendChild(prev_button_text);
    prev_button.addEventListener('click', displayPrevInstance);
    prev_next_group.appendChild(prev_button);
    // Next button
    var next_button = document.createElement('button');
    next_button.setAttribute('class', 'btn btn-' + type);
    next_button.setAttribute('type', 'button');
    next_button.setAttribute('id', 'next_button');
    var next_button_text = document.createTextNode('Next');
    next_button.appendChild(next_button_text);
    next_button.addEventListener('click', displayNextInstance);
    prev_next_group.appendChild(next_button);
}
