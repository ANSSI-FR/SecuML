var project       = window.location.pathname.split('/')[2];
var dataset       = window.location.pathname.split('/')[3];
var experiment_id = window.location.pathname.split('/')[4];
var iteration     = window.location.pathname.split('/')[5];

generateDivisions();
displayFamilies('malicious');
displayFamilies('benign');

function displayFamilies(label) {
    var query = buildQuery('getFamiliesBarplot',
                           [project, dataset, experiment_id, iteration, label]);
    var div = $('#' + label)[0];
    $.getJSON(query, function (data) {
        var options = barPlotOptions(data, 'Families');
        var barPlot = drawBarPlot(label,
                                   options, data);
        div.style.height = '600px';
        div.style.width = '1200px';
    });
}

function generateDivisions() {
  var main = document.getElementById('main');

  var menu_labels = ['malicious', 'benign'];
  var menu_titles = ['Malicious', 'Benign'];
  var menu = createTabsMenu(menu_labels, menu_titles,
          parent_div = main);
}
