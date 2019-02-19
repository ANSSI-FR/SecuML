var path            = window.location.pathname.split('/');
var exp_id          = path[2];
var iteration = path[3];
var exp_type        = 'ActiveLearning';
var label_method    = 'annotation';

var instances_list         = null;
var num_instances          = null;
var current_instance_index = null;

var conf = null;

function getCurrentInstance() {
    return instances_list[current_instance_index];
}

function callback(conf) {
    conf.interactive = false;
    if (!conf.core_conf.auto) {
        var current_iteration = currentAnnotationIteration(exp_id);
        conf.interactive = iteration == current_iteration;
    }
    displayDivisions(conf);
    displayInstancesToAnnotate();
    addShortcuts();
}

loadConfigurationFile(exp_id, callback);

function displayInstancesToAnnotate() {
    var query = buildQuery('getInstancesToAnnotate',
            [exp_id, iteration, 'None']);
    d3.json(query, function(data) {
        instances_list = data['instances'];
        current_instance_index = 0;
        num_instances = instances_list.length;
        var iter_label = cleanDiv('iter_label');
        iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
        printInstanceInformation(instances_list[current_instance_index]);
    });
}

function displayNextInstance() {
    if (current_instance_index <= num_instances-2) {
        current_instance_index += 1;
        var iter_label = cleanDiv('iter_label');
        iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
        printInstanceInformation(instances_list[current_instance_index]);
    }
}

function displayNextInstanceToAnnotate() {
    displayNextInstance();
}

function displayPrevInstance() {
    if (current_instance_index > 0) {
        current_instance_index -= 1;
        var iter_label = cleanDiv('iter_label');
        iter_label.appendChild(document.createTextNode((current_instance_index+1) + ' / ' + num_instances));
        printInstanceInformation(instances_list[current_instance_index]);
    }
}

function displayDivisions(conf) {
    var main = $('#main')[0];

    // Navigation bar
    var row = createDivWithClass(null,  'row', parent_div = main);
    var panel_body = createPanel('panel-primary', 'col-md-12', null, row);
    var annotation_query_label = document.createElement('label');
    annotation_query_label.setAttribute('class', 'col-lg-2 control-label');
    annotation_query_label.appendChild(document.createTextNode('Annotation Query'));
    panel_body.appendChild(annotation_query_label);
    var iter_label = document.createElement('label');
    iter_label.setAttribute('class', 'col-lg-1 control-label');
    iter_label.setAttribute('id', 'iter_label');
    panel_body.appendChild(iter_label);
    // Prev / Next buttons
    var prev_next_group = createDivWithClass('', 'form-group col-md-3', panel_body);

    var prev_button = document.createElement('button');
    prev_button.setAttribute('class', 'btn btn-primary');
    prev_button.setAttribute('type', 'button');
    prev_button.setAttribute('id', 'prev_button');
    var prev_button_text = document.createTextNode('Prev');
    prev_button.appendChild(prev_button_text);
    prev_button.addEventListener('click', displayPrevInstance);
    prev_next_group.appendChild(prev_button);

    var next_button = document.createElement('button');
    next_button.setAttribute('class', 'btn btn-primary');
    next_button.setAttribute('type', 'button');
    next_button.setAttribute('id', 'next_button');
    var next_button_text = document.createTextNode('Next');
    next_button.appendChild(next_button_text);
    next_button.addEventListener('click', displayNextInstance);
    prev_next_group.appendChild(next_button);

    // End annotation process
    if (conf.interactive) {
        var end_group = createDivWithClass('', 'form-group col-md-3', panel_body);
        var end_button = document.createElement('button');
        end_button.setAttribute('class', 'btn btn-primary');
        end_button.setAttribute('type', 'button');
        end_button.setAttribute('id', 'end_button');
        var end_button_text = document.createTextNode('Next Iteration');
        end_button.appendChild(end_button_text);
        end_button.addEventListener('click', runNextIteration(conf));
        end_group.appendChild(end_button);
    }

    displayAnnotationDivision(false);
}
