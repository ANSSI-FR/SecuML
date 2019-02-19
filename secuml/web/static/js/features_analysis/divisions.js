function generate_divisions(conf) {
    generateTitle('Features Analysis');
    generate_sorting_criterion_selector(conf);
}

function generate_sorting_criterion_selector(conf) {
    var col_sorting = $('#col_sorting')[0];
    var query = buildQuery('getSortingCriteria', [exp_id]);
    $.getJSON(query, function(data) {
        var criteria = data.criteria;
        var select_sorting_div = createDiv('select_sorting_div',
                                            parent_div=col_sorting);
        var sorting_selector = createSelectList('sorting_selector',
                                                criteria.length,
                                                display_sorted_features,
                                                select_sorting_div,
                                                label='Sorting Criterion');
        addElementsToSelectList('sorting_selector', criteria);
        // Callback
        generate_feature_selector();
        generate_plots_panel();
    });
}

function generate_feature_selector() {
    var col_features = $('#col_features')[0];
    var select_features_div = createDiv('select_features_div',
                                        parent_div=col_features);
    var features_selector = createSelectList('features_selector', 10,
                                             display_feature,
                                             select_features_div,
                                             label='Features',
                                             multiple=false,
                                             with_search=true);
}

function generate_plots_panel() {
    var plots_col = $('#col_stats')[0];
    var panel = createPanel('panel-primary', null, 'Feature', plots_col,
                            'menu_div', return_heading=true);
    var feature_title = panel[1];
    feature_title.setAttribute('id', 'feature_title');
    var menu = createTabsMenu(['boxplot', 'hist', 'density', 'scores'],
                              ['Boxplot', 'Histogram', 'Density', 'Scores'],
                              panel[0]);
}

function create_tabs_structure() {
    create_scores_table();
    create_pictures();
}

function create_scores_table() {
    var scores = document.getElementById('scores');
    var header = ['Criterion', 'Value', 'Rank'];
    var body = createTable('scores', header, table_id='scores_tab');
    var feature_1 = Object.keys(features_info)[0];
    var query = buildQuery('getFeatureScores', [exp_id, feature_1]);
    $.getJSON(query, function (data) {
        var criteria = Object.keys(data);
        criteria.sort();
        for (var i = 0; i < criteria.length; i++) {
            var criterion = criteria[i];
            addRow(body,
                   [criterion, '', ''],
                   ids=[null, criterion + '_value', criterion + '_rank'],
                   title=false,
                   row_class=null);
        }
    });
}

function create_pictures() {
    // Density
    var density = cleanDiv('density');
    var picture = document.createElement('img');
    picture.setAttribute('class', 'img-responsive');
    picture.setAttribute('id', 'density_picture');
    density.appendChild(picture);
    // Boxplot
    var boxplot = cleanDiv('boxplot');
    var picture = document.createElement('img');
    picture.setAttribute('class', 'img-responsive');
    picture.setAttribute('id', 'boxplot_picture');
    boxplot.appendChild(picture);
}
