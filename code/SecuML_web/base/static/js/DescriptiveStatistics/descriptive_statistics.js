var path = window.location.pathname.split('/');
var project       = path[2];
var dataset       = path[3];
var experiment_id = path[4];
var init_feature  = path[5];

var features_types =  null;

loadConfigurationFile(project, dataset, experiment_id, callback);

function loadConfigurationFile(project, dataset, experiment_id, callback) {
  $.getJSON(buildQuery('getConf',
                     [project, dataset, experiment_id]),
          function(data) {
              var conf = data;
              callback(conf);
          });
}

function callback(conf) {
  generateDivisions(conf);
  loadFeaturesNames();
}

function displaySelectedFeature() {
  if (init_feature != '') {
      $('#features_selector').val(init_feature);
  } else {
      $('#features_selector')[0].selectedIndex = 0;
  }
  displayFeatureAnalysis();
}

function generateDivisions(conf) {
  var col1 = $('#col1')[0];
  var select_features_div = createDiv('select_features_div', parent_div = col1);
  var features_selector = createSelectList('features_selector', 5, displayFeatureAnalysis, select_features_div,
          label = 'Features');
  var plots_col = $('#col2')[0];
  var menu_div = createDiv('menu_div', parent_div = plots_col);
}

function loadFeaturesNames() {
  var query = buildQuery('getFeaturesTypes',
                         [project, dataset, experiment_id]);
  $.getJSON(query, function(data) {
      var features = data['features'];
      addElementsToSelectList('features_selector', features);
      var features_selector = $('#features_selector')[0];
      features_types = data['types'];
      displaySelectedFeature();
  });
}

function displayFeatureAnalysis() {
  var menu_div = cleanDiv('menu_div');
  var selected_feature = getSelectedOption($('#features_selector')[0]);
  var type    = features_types[selected_feature];
  if (type == 'binary') {
    displayBinaryFeatureAnalysis(selected_feature, menu_div);
  } else if (type == 'numeric') {
    displayNumericFeatureAnalysis(selected_feature, menu_div);
  }
}

function displayBinaryFeatureAnalysis(feature, menu_div) {
  var menu = createTabsMenu(['bin_hist'], ['Histogram'],
                            menu_div);
  // Histogram
  var query = buildQuery('getStatsPlot',
                         [project, dataset, experiment_id, 'binary_histogram', feature]);
  var bin_hist = $('#bin_hist')[0];
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data);
      var barPlot = drawBarPlot('bin_hist',
                                 options, data);
      bin_hist.style.height = '400px';
  });
}

function displayNumericFeatureAnalysis(feature, menu_div) {
  var menu = createTabsMenu(['boxplot', 'hist', 'density'],
                            ['Boxplot', 'Histogram', 'Density'],
                            menu_div);
  // BoxPlot
  var boxplot = document.getElementById('boxplot');
  var path = buildQuery('getStatsPlot',
                        [project, dataset, experiment_id, 'boxplot', feature]);
  var picture = document.createElement('img');
  picture.src = path;
  picture.style.width = '80%';
  picture.style.height = 'auto';
  boxplot.appendChild(picture);
  // Histogram
  var hist = document.getElementById('hist');
  hist.setAttribute('class', 'tab-pane fade');
  var query = buildQuery('getStatsPlot',
                         [project, dataset, experiment_id, 'histogram', feature]);
  var hist = $('#hist')[0];
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data);
      var barPlot = drawBarPlot('hist',
                                 options, data);
      hist.style.height = '400px';
  });
  // Density
  var density = document.getElementById('density');
  var path = buildQuery('getStatsPlot',
                        [project, dataset, experiment_id, 'density', feature]);
  var picture = document.createElement('img');
  picture.src = path;
  picture.style.width = '80%';
  picture.style.height = 'auto';
  density.appendChild(picture);
}
