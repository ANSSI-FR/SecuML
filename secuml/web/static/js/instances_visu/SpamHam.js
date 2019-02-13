var mail_text = null;

function specificTabs() {
    var menu_titles = ['Mail'];
    var menu_labels = ['mail'];
    return [menu_titles, menu_labels];
}

function initTabs() {
  var div_object = cleanDiv('mail');
  div_object.style.overflow = 'auto';
  div_object.style.whiteSpace = 'pre-wrap';
  var div_height = Math.round(window.screen.availHeight * 0.4) + 'px';
  div_object.style.height = div_height;
}

function printSpecificInformations(selected_id) {
  printMail(selected_id);
}

function cleanSpecificInformations() {
    document.getElementById('mail').textContent = '';
}

function printMail(selected_id) {
  var query = buildQuery('getInstance', [exp_id, 'None', selected_id]);
  $.get(query, function(data) {
      document.getElementById('mail').textContent = data;
  });
}
