function interactiveAnnotations() {
    return !(annotations_type == 'ground_truth');
}



// Display a list of instances

function updateList(query) {
    $.getJSON(query,
        function(data) {
            instances_list = data['instances'];
            proba_list = data['proba'];
            scores_list = data['scores'];
            ranking = data['ranking'];
            current_instance_index = 0;
            num_instances = instances_list.length;
            var num_instances_label = document.getElementById('num_instances_label');
            num_instances_label.textContent = num_instances;
            var curr_instance_label = document.getElementById('curr_instance_label');
            if (num_instances > 0) {
                curr_instance_label.value = current_instance_index + 1;
                displayInstance(current_instance_index);
            } else {
                curr_instance_label.value = '0';
                cleanInstanceData();
                undisplayAnnotation();
            }
        }
        );
}

function displayCurrentInstance() {
    var new_index = document.getElementById('curr_instance_label').value;
    if (new_index >= 1 && new_index <= num_instances) {
        current_instance_index = new_index - 1;
        displayInstance(current_instance_index);
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
        update_curr_instance_label(current_instance_index);
        displayInstance(current_instance_index);
    }
}

function displayPrevInstance() {
    if (current_instance_index > 0) {
        current_instance_index -= 1;
        update_curr_instance_label(current_instance_index);
        displayInstance(current_instance_index);
    }
}

function displayInstance(current_instance_index) {
    printInstanceInformation(instances_list[current_instance_index],
                             proba_list[current_instance_index],
                             scores_list[current_instance_index],
                             ranking[current_instance_index]);
}

function update_curr_instance_label(current_instance_index) {
    var curr_instance_label = document.getElementById('curr_instance_label');
    curr_instance_label.value = current_instance_index + 1;
}
