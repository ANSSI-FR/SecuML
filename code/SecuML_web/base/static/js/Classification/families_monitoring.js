function displayFamiliesTabs(div_name, project, dataset, experiment_id, train_test) {
  var global_div = cleanDiv(div_name);

  // Tabs menu
  var menu_labels = ['malicious_families',
                     'benign_families'];
  var menu_titles = ['Malicious', 'Benign'];
  var menu = createTabsMenu(menu_labels, menu_titles,
          parent_div = global_div);

  // Tabs content
  var tabs_content = createDivWithClass(
          'families_tab_content',
          'tab-content',
          parent_div = global_div);
  // Malicious
  var malicious_families = createDivWithClass(
          'malicious_families',
          'tab-pane fade in active',
          parent_div = tabs_content);
  displayFamiliesPerformance(project, dataset, experiment_id, train_test, 'malicious');
  // Benign
  var benign_families = createDivWithClass(
          'benign_families',
          'tab-pane fade',
          parent_div = tabs_content);
  displayFamiliesPerformance(project, dataset, experiment_id, train_test, 'benign');
}

function displayFamiliesPerformance(project, dataset, experiment_id, train_test, label) {
    var threshold = $('#slider').slider('value');
    var perf_div_name = label + '_families';
    var perf_div = cleanDiv(perf_div_name);
    var query = buildQuery('getFamiliesPerformance',
                           [project, dataset, experiment_id, train_test, label, threshold]);
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data);
      var barPlot = drawBarPlot(perf_div_name,
                                 options, data);
      perf_div.style.height = '800px';
      perf_div.style.width = '1200px';
  });

}

function displayFamiliesMonitoring(conf, train_test, sup_exp) {
  var exp = conf.experiment_id;
  if (sup_exp) {
    exp = sup_exp;
  }
  var div = cleanDiv(train_test + '_families');
  var elem = document.createElement('a');
  var text = document.createTextNode('Display detection rates / false alarm rates');
  elem.appendChild(text);
  var query = buildQuery('familiesPerformance',
                         [conf.project, conf.dataset, exp, train_test]);
  elem.setAttribute('href', query);
  div.appendChild(elem);
}
