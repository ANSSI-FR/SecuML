var path = window.location.pathname.split('/');
var exp_id = path[2];
var init_feature = path[3];

var features_info = null;
var selected_criterion = null;
var user_ids = null;
var values = null;
var pvalues = null;
var binary = false;
var conf = null;


function callback(conf) {
    conf.has_ground_truth = conf.dataset_conf.has_ground_truth;
    generate_divisions(conf);
    load_features_info();
}

loadConfigurationFile(exp_id, callback);

function display_selected_feature() {
    if (init_feature != '') {
        $('#features_selector').val(init_feature);
        init_feature = '';
    } else {
        $('#features_selector')[0].selectedIndex = 0;
    }
    display_feature();
}

function load_features_info() {
    var query = buildQuery('getFeaturesInfo', [exp_id]);
    $.getJSON(query, function(data) {
        features_info = data;
        $('#sorting_selector').val('alphabet');
        create_tabs_structure();
        display_sorted_features();
    });
}

function display_sorted_features() {
    selected_criterion = getSelectedOption($('#sorting_selector')[0]);
    var query = buildQuery('getSortedFeatures', [exp_id,
                                                 selected_criterion]);
    $.getJSON(query, function(data) {
        var features = data.features;
        user_ids = data.user_ids;
        values = data.values;
        pvalues = data.pvalues;
        addElementsToSelectList('features_selector', features, text=user_ids);
        if (features.length > 0) {
            display_selected_feature();
        } else {
            if (selected_criterion == 'null_variance') {
                displayAlert('no_null_var', 'No feature with null variance',
                             ['All features have a non null variance.'])
            }
        }
    });
    //display_criterion_density(selected_criterion);
}

function display_criterion_density(criterion) {
    var graph_div = cleanDiv('col_graph');
    if (criterion == 'alphabet') {
        return;
    }
    var path = buildQuery('getCriterionDensity', [exp_id, criterion]);
    var picture = document.createElement('img');
    picture.setAttribute('class', 'img-responsive');
    picture.src = path;
    picture.style.width = 'auto';
    picture.style.height = 'auto';
    graph_div.appendChild(picture);
}

function display_feature() {
    var selected_feature = getSelectedOption($('#features_selector')[0]);
    display_feature_analysis(selected_feature);
    display_feature_description(selected_feature);
}

function display_feature_analysis(selected_feature) {
    var feature_title = selected_feature;
    if (values != null) {
        var feature_index = $('#features_selector')[0].selectedIndex;
        var title_elem = [feature_title, ' - ', selected_criterion, ': ',
                          values[feature_index]]
        if (pvalues != null) {
            title_elem = title_elem.concat([' (p-value: ',
                                            pvalues[feature_index],
                                            ')']);
        }
        feature_title = title_elem.join('');
    }
    document.getElementById('feature_title').textContent = feature_title;
    var type = features_info[selected_feature].type;
    if (type == 'binary') {
        display_binary_feature_analysis(selected_feature);
    } else if (type == 'numeric') {
        display_numeric_feature_analysis(selected_feature);
    }
}

function display_binary_feature_analysis(feature) {
    display_binary_histogram(feature);
    display_scores(feature);
    var boxplot = document.getElementById('boxplot');
    boxplot.innerHTML = 'Unavailable for binary features';
    var density = document.getElementById('density');
    density.innerHTML = 'Unavailable for binary features';
    binary = true;
}

function display_numeric_feature_analysis(feature) {
    if (binary) {
        create_pictures();
    }
    display_boxplot(feature);
    display_histogram(feature);
    display_density(feature);
    display_scores(feature);
    binary = false;
}

function display_boxplot(feature) {
    var picture = document.getElementById('boxplot_picture');
    var path = buildQuery('getStatsPlot', [exp_id, 'boxplot', feature]);
    picture.src = path;
}

function display_histogram(feature) {
    var query = buildQuery('getStatsPlot', [exp_id, 'histogram',
                                            feature]);
    var hist = $('#hist')[0];
    $.getJSON(query, function (data) {
        var options = barPlotOptions(data);
        var barPlot = drawBarPlot('hist', options, data);
        hist.style.height = '350px';
    });
}

function display_binary_histogram(feature) {
    var query = buildQuery('getStatsPlot', [exp_id, 'binary_histogram',
                                            feature]);
    var hist = $('#hist')[0];
    $.getJSON(query, function (data) {
        var options = barPlotOptions(data);
        var barPlot = drawBarPlot('hist', options, data);
        hist.style.height = '400px';
    });
}

function display_density(feature) {
    var picture = document.getElementById('density_picture');
    var path = buildQuery('getStatsPlot', [exp_id, 'density', feature]);
    picture.src = path;
}

function display_scores(feature) {
    var body = document.getElementById('scores_tab');
    var query = buildQuery('getFeatureScores', [exp_id, feature]);
    $.getJSON(query, function (data) {
        var criteria = Object.keys(data);
        for (var i = 0; i < criteria.length; i++) {
            var criterion = criteria[i];
            var value_elem = document.getElementById(criterion + '_value');
            value_elem.innerHTML = data[criterion].value;
            var rank_elem = document.getElementById(criterion + '_rank');
            rank_elem.innerHTML = data[criterion].rank;
        }
    });
}

function display_feature_description(feature) {
    var col_description = cleanDiv('col_description');
    var info = features_info[feature]
    if (info.description == null) {
        return;
    }
    var title = info.name;
    var panel = createPanel('panel-primary', null, title, col_description,
                            'description_div', return_heading=true);
    var description_div = panel[0];
    description_div.style.whiteSpace = 'pre';
    var description_title = panel[1];
    description_title.setAttribute('id', 'description_title');
    description_div.innerHTML = info.description;
}
