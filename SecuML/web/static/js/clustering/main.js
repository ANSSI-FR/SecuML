var path = window.location.pathname.split('/');
var experiment_id = path[2];
var exp_type = 'Clustering';

var label_iteration = 0;
var label_method = 'clustering';
var num_results = 10;

var last_instance_selector = null;
var current_cluster_label  = null;
var current_cluster_family = null;

var clusters_labels = null;

function getCurrentInstance() {
    return getSelectedOption(last_instance_selector);
}

function loadConfigurationFile(experiment_id, callback) {
    $.getJSON(buildQuery('getConf', [experiment_id]),
            function(data) {
                conf = data;
                conf.has_ground_truth = conf.dataset_conf.has_ground_truth;
                setInstancesSettings('train', experiment_id);
                callback(conf);
            }
            );
}

var conf = {}
loadConfigurationFile(experiment_id, onceConfigurationIsLoaded);

function displayClusterIdSelection() {
    var callback = function() {
        var selected_cluster = getSelectedOption(select_cluster_id);
        displayCluster(selected_cluster);
    }
    var cluster_id_div = cleanDiv('cluster_id');
    var select = createSelectList('select_cluster_id', 5, callback,
                                  parent_div=cluster_id_div);
    var get_labels  = buildQuery('getClustersLabels', [experiment_id]);
    $.getJSON(get_labels,
            function(data) {
                clusters_labels = data.clusters;
                // Display the selector for the cluster index
                for (var c = 0; c < clusters_labels.length; c++) {
                    var opt = document.createElement('option');
                    opt.text = clusters_labels[c].label;
                    opt.value = clusters_labels[c].id;
                    select_cluster_id.add(opt);
                }
                // Display the first cluster
                select.selectedIndex = 0;
                displayCluster(0);
            }
            );
}

function onceConfigurationIsLoaded(conf) {
    generateClusteringDivisions();
    displayClusterIdSelection();
    displayClustersStats(conf);
}

function displayClustersStats(conf) {
    var callback = function(active_bars) {
        var selected_index = active_bars[0]._index;
        var selected_cluster = active_bars[0]._view.label.split('_')[1];
        document.getElementById('select_cluster_id').selectedIndex = selected_index;
        var selected_cluster = getSelectedOption(select_cluster_id);
        displayCluster(selected_cluster);
    }
    var query = buildQuery('getClusterStats', [experiment_id]);
    var clusters_stats = $('#clusters_labels_stats')[0];
    $.getJSON(query, function (data) {
        var options = barPlotOptions(data);
        options.responsive = false;
        var bar_plot = drawBarPlot('clusters_labels_stats',
                                   options, data,
                                   type = 'bar',
                                   width = '550',
                                   height = '250',
                                   callback = callback);
    });
}

function displayCluster(selected_cluster) {
    cleanCluster();
    displayNumElements(experiment_id, selected_cluster);
    displayClusterInstances(selected_cluster);
}

function displayClusterInstances(selected_cluster) {
    displayClusterInstancesByPosition(selected_cluster);
    displayClusterInstancesByFamily(selected_cluster);
}

function cleanCluster() {
    cleanDiv('instances_by_label');
    cleanDiv('instances_by_position');
    displayAnnotationDiv();
    cleanInstanceData();
}

function displayClusterInstancesByFamily(selected_cluster) {
    createPerLabelSelectors('Families');
    var label_selector = $('#select_labels')[0];
    var instance_selector = $('#select_instances_label_family')[0];
    var query = buildQuery('getClusterLabelsFamilies',
                           [experiment_id, selected_cluster]);
    $.getJSON(query,
            function(data) {
                labels_families = [];
                labels = Object.keys(data);
                for (var l in labels) {
                    label = labels[l];
                    families = Object.keys(data[label]);
                    for (var q in families) {
                        family = families[q];
                        labels_families.push(label + '-' + family);
                    }
                }
                labels_families.push('unlabeled');
                addElementsToSelectList('select_labels', labels_families);
            }
            );
    label_selector.addEventListener('change', function() {
        cleanDiv('select_instances_label_family');
        selected_label_family = getSelectedOption(label_selector);
        var split = selected_label_family.split('-')
        var selected_label = split[0];
        if (selected_label != 'unlabeled') {
            var selected_family = split.slice(1, split.length).join('-');
        } else {
            var selected_family = 'None';
        }
        var query = buildQuery('getClusterLabelFamilyIds',
                               [experiment_id, selected_cluster, selected_label,
                                selected_family, num_results]);
        $.getJSON(query, function(data) {
                    console.log(query);
                    console.log(data);
                    addElementsToSelectList('select_instances_label_family',
                                            data.ids);
                });
    });
}

function displayClusterInstancesByPosition(selected_cluster) {
    var instances_div = cleanDiv('instances_by_position');
    var position_label = createDivWithClass('position_label_div', 'row',
                                            parent_div=instances_div);
    var titles = ['Center', 'Edge', 'Random'];
    var selects = ['center', 'edge', 'random'];
    for (var i = 0; i < titles.length; i++) {
        var pos = selects[i];
        var select_position_div = createDivWithClass('None', 'col-md-4',
                parent_div=instances_div);
        var select = createSelectList('select_' + pos + '_instances',
                5,
                function () {
                    selected_instance_id = getSelectedOption(this);
                    printInstanceInformation(selected_instance_id, '');
                    last_instance_selector = this;
                    // unselect other position selectors
                    for (var j = 0; j < titles.length; j++) {
                        var p = selects[j];
                        var s = document.getElementById('select_' + p + '_instances');
                        if (s != this) {
                            s.selectedIndex = -1;
                        }
                    }
                },
                select_position_div,
                titles[i]);
        displayInstancesInOneSelector(selected_cluster, pos);
    }
}

function displayNumElements(experiment, selected_cluster) {
    var query = buildQuery('getNumElements', [experiment_id, selected_cluster]);
    $.getJSON(query,
            function(data) {
                var num_elements = data.num_elements;
                $('#cluster_info_id')[0].firstChild.nodeValue = clusters_labels[selected_cluster].label;
                var elements = ' element';
                if (num_elements > 1) {
                    elements += 's';
                }
                $('#cluster_info_num_elements')[0].firstChild.nodeValue = num_elements + elements;
            }
            );
}

function displayInstancesInOneSelector(selected_cluster, c_e_r) {
    // Get the ids belonging to the selected cluster
    var instance_selector = null;
    if (c_e_r == 'center') {
        instance_selector = 'select_center_instances';
    } else if (c_e_r == 'edge') {
        instance_selector = 'select_edge_instances';
    } else if (c_e_r == 'random') {
        instance_selector = 'select_random_instances';
    }
    var query = buildQuery('getClusterInstancesVisu',
            [experiment_id, selected_cluster, c_e_r[0],
             num_results]);
    $.getJSON(query,
            function(data) {
                ids = data[selected_cluster];
                addElementsToSelectList(instance_selector, ids);
                if (c_e_r == 'center') {
                    // Display the first instance
                    if (ids.length > 0) {
                        instance_selector.selectedIndex = 0;
                        printInstanceInformation(ids[0], '');
                        last_instance_selector = instance_selector;
                    }
                }
            }
            );
}
