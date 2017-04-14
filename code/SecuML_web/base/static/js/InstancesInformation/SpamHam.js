var last_selected_id = null;

function specificTabs() {
    var menu_titles = ['Mail'];
    var menu_labels = ['mail'];
    return [menu_titles, menu_labels];
}

function printSpecificInformations(selected_id, ident) {
  printMail(selected_id, ident);
}

function cleanInformation() {
    cleanDiv('instance_data_div');
}

function printMail(selected_id, ident) {
  var div_object = cleanDiv('mail');
  var query = buildQuery('getInstance',
              [project, inst_dataset, selected_id, ident]);
  $.get(query, function(data) {
      var mail = document.createTextNode(data);
      div_object.appendChild(mail);
  });
}
