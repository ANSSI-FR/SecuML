function hasTrueLabels(project, dataset) {
  var query = buildQuery('hasTrueLabels', [project, dataset]);
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open('GET', query, false);
  xmlHttp.send(null);
  var has_true_labels = xmlHttp.responseText;
  return has_true_labels == 'True';
}

function addRemoveLabels(div_name, add_function, remove_function) {
  cleanDiv(div_name);
  //// Remove button  
  var button_remove = document.createElement('button');
  button_remove.appendChild(document.createTextNode('Remove'));
  button_remove.addEventListener('click', remove_function);
  var div_remove = document.createElement('div');
  div_remove.appendChild(button_remove);
  $('#' + div_name)[0].appendChild(div_remove);
  //// Add button
  var label = document.createElement('input');
  label.setAttribute('size', 7);
  var sublabel = document.createElement('input');
  sublabel.setAttribute('size', 7);
  var button_add = document.createElement('button');
  button_add.appendChild(document.createTextNode('Add'));
  button_add.addEventListener('click', function() {
      var label_value = label.value;
      var sublabel_value = sublabel.value;
      if (sublabel_value == '') {
          sublabel_value = 'other';
      }
      add_function(label_value, sublabel_value);
  });
  var div_add = document.createElement('div');
  div_add.appendChild(label);
  div_add.appendChild(sublabel);
  div_add.appendChild(button_add);
  $('#' + div_name)[0].appendChild(div_add);
}
