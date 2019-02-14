var path = window.location.pathname.split('/');
var exp_id = path[2];
var selected_kind = path[3];

var label_method = 'confusion_matrix';
var iteration = 0;

var exp_type               = 'Predictions';
var instances_list         = null;
var proba_list             = null;
var current_instance_index = null;

var errors = {'fp': null,
    'fn': null};
var titles = {'fp': 'False Positives',
    'fn': 'Undetected'};

function getCurrentInstance() {
    return instances_list[current_instance_index];
}

var conf = null;

function callback(conf) {
    conf.has_ground_truth = conf.dataset_conf.has_ground_truth;
    displayDivisions(selected_kind);
    updateInstancesDisplay(exp_id, selected_kind);
    addPrevNextShortcuts();
}

loadConfigurationFile(exp_id, callback);

function updateInstancesDisplay(exp_id, label) {
    if (!label) {
        label = 'all';
    }
    var query = buildQuery('supervisedLearningMonitoring', [conf.exp_id,
                                                            'errors']);
    $.getJSON(query,
            function(data) {
                if (label == 'all') {
                    instances_list = data['FP']['ids'].concat(data['FN']['ids']);
                    proba_list = data['FP']['probas'].concat(data['FN']['probas']);
                } else {
                    instances_list = data[label]['ids'];
                    proba_list = data[label]['probas']
                }
                current_instance_index = 0;
                num_instances = instances_list.length;
                var num_instances_label = document.getElementById('num_instances_label');
                num_instances_label.textContent = num_instances;
                var curr_instance_label = document.getElementById('curr_instance_label');
                if (num_instances > 0) {
                    curr_instance_label.value = current_instance_index + 1;
                    printInstanceInformation(instances_list[current_instance_index],
                                             proba_list[current_instance_index]);
                } else {
                    curr_instance_label.value = '0';
                    cleanInstanceData();
                    undisplayAnnotation();
                }
            });
}

function displayDivisions(selected_kind) {
    var main = $('#main')[0];

    // Navigation bar
    var row = createDivWithClass(null,  'row', parent_div=main);
    row.setAttribute('id', 'navigation_row');
    displayNavigationPanel(selected_kind);

    // Selected instance - data and annotation
    var row = createDivWithClass(null, 'row', parent_div=main);
    displayInstancePanel(row);
    displayInstanceInformationStructure();
    displayAnnotationDiv(false, interactiveAnnotations());
}

function displayNavigationPanel(selected_kind) {
    var parent_div = cleanDiv('navigation_row');
    var panel_body = createPanel('panel-primary', 'col-md-12',
            'Detection Errors', parent_div);
    // Select kind of errors (all, FP, or FN)
    var select_col = createDivWithClass(null, 'col-md-3',
            parent_div=panel_body);
    labels = ['all', 'FP', 'FN'];
    labels_ids = ['errors_all', 'errors_FP', 'errors_FN'];
    function radio_callback() {
        updateInstancesDisplay(exp_id,
                               getSelectedRadioButton(labels_ids));
    }
    createRadioList('error_radio', labels, labels_ids, radio_callback,
                    select_col, 'errors_' + selected_kind);

    // Go trough the selected instances
    var form_group = createDivWithClass(null, 'col-md-9 form-group',
            parent_div=panel_body);
    var navig_col = createDivWithClass(null, 'row input-group',
            parent_div=form_group);

    var annotation_query_label = document.createElement('label');
    annotation_query_label.setAttribute('class', 'col-md-2 control-label');
    annotation_query_label.appendChild(document.createTextNode('Instance'));
    navig_col.appendChild(annotation_query_label);

    var curr_instance_div = createDivWithClass(null, 'col-md-2',
            parent_div=navig_col);
    var curr_instance_label = document.createElement('input');
    curr_instance_label.setAttribute('class', 'form-control');
    curr_instance_label.setAttribute('id', 'curr_instance_label');
    curr_instance_label.setAttribute('type','text');
    curr_instance_div.appendChild(curr_instance_label);

    var over_label = document.createElement('label');
    over_label.setAttribute('class', 'col-md-1 control-label');
    over_label.textContent = '/';
    navig_col.appendChild(over_label);

    var num_instances_label = document.createElement('label');
    num_instances_label.setAttribute('class', 'col-md-1 control-label');
    num_instances_label.setAttribute('id', 'num_instances_label');
    navig_col.appendChild(num_instances_label);

    // OK / Prev / Next buttons
    // Ok
    var button_div = createDivWithClass(null, 'col-md-2', parent_div=navig_col);
    var button = document.createElement('button');
    button.setAttribute('class', 'btn btn-primary');
    button.setAttribute('type', 'button');
    var button_text = document.createTextNode('Ok');
    button.appendChild(button_text);
    button.addEventListener('click', displayCurrentInstance);
    button_div.appendChild(button);
    // Prev
    var button_div = createDivWithClass(null, 'col-md-2', parent_div=navig_col);
    var button = document.createElement('button');
    button.setAttribute('class', 'btn btn-primary');
    button.setAttribute('type', 'button');
    button.setAttribute('id', 'prev_button');
    var button_text = document.createTextNode('Prev');
    button.appendChild(button_text);
    button.addEventListener('click', displayPrevInstance);
    button_div.appendChild(button);
    // Next
    var button_div = createDivWithClass(null, 'col-md-2', parent_div=navig_col);
    var button = document.createElement('button');
    button.setAttribute('class', 'btn btn-primary');
    button.setAttribute('type', 'button');
    button.setAttribute('id', 'next_button');
    var button_text = document.createTextNode('Next');
    button.appendChild(button_text);
    button.addEventListener('click', displayNextInstance);
    button_div.appendChild(button);
}

function displayCurrentInstance() {
    var new_index = document.getElementById('curr_instance_label').value;
    if (new_index >= 1 && new_index <= num_instances) {
        current_instance_index = new_index - 1;
        printInstanceInformation(instances_list[current_instance_index],
                proba_list[current_instance_index]);
    } else {
        if (num_instances > 0) {
            displayAlert('wrong_index_alert', 'Wrong Index',
                    ['The index must be between 1 and ' + num_instances]);
        } else {
            displayAlert('wrong_index_alert', 'Wrong Index',
                    ['There is no instance to display.']);
        }
    }
}

function displayNextInstance() {
    if (current_instance_index <= num_instances-2) {
        current_instance_index += 1;
        var curr_instance_label = document.getElementById('curr_instance_label');
        curr_instance_label.value = current_instance_index + 1;
        printInstanceInformation(instances_list[current_instance_index],
                proba_list[current_instance_index]);
    }
}

function displayPrevInstance() {
    if (current_instance_index > 0) {
        current_instance_index -= 1;
        var curr_instance_label = document.getElementById('curr_instance_label');
        curr_instance_label.value = current_instance_index + 1;
        printInstanceInformation(instances_list[current_instance_index],
                proba_list[current_instance_index]);
    }
}
