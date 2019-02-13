var path = window.location.pathname.split('/');
var exp_id = path[2];
var conf = null;


loadConfigurationFile(exp_id, displayDivisions);

function displayFamilySelector(label_row, label, multiple, families_values) {
  var col = createDivWithClass(null, 'col-md-5', parent_div = label_row);
  // Selection
  var select = $('#' + label + '_family_selector')[0];
  var label_title = [label.charAt(0).toUpperCase(), label.substr(1),
                     ' Families'].join('');
  var selector_size = 6;
  createSelectList(label + '_family_selector', selector_size, null, col,
                   label_title, multiple);
  var select = $('#' + label + '_family_selector')[0];
  // Family values
  var select = $('#' + label + '_family_selector')[0];
  var families = Object.keys(families_values[label]);
  families.forEach(function(q) {
      addElementToSelectList(select, q);
  });
  // Add family selector callback
  select.addEventListener('change', familyChangeCallback(label));
  return col;
}

function familyChangeCallback(selected_label) {
    return function() {
      // Unselect the family of the other label
      var other_label = otherLabel(selected_label);
      var other_selector = $('#' + other_label + '_family_selector')[0];
      other_selector.selectedIndex = -1;
    }
}

function displayFamiliesSelectors(panel, multiple=false) {
  var label_div = createDiv('families', panel);
  var form = document.createElement('form');
  form.setAttribute('class', 'form-horizontal');
  label_div.appendChild(form);
  var fieldset = document.createElement('fieldset');
  form.appendChild(fieldset);
  var query = buildQuery('getLabelsFamilies', ['partial', annotations_id,
                                               dataset_id, 'None']);
  jQuery.getJSON(query, function(data) {
        var malicious_col = displayFamilySelector(fieldset, 'malicious',
                                                  multiple, data);
        var col = createDivWithClass(null, 'col-md-1', parent_div = fieldset);
        var benign_col = displayFamilySelector(fieldset, 'benign', multiple,
                                               data);
  });

}

function getSelectedFamily() {
  var malicious_selector = $('#malicious_family_selector')[0];
  var benign_selector    = $('#benign_family_selector')[0];
  if (malicious_selector.selectedIndex != -1) {
      var label = 'malicious';
      var family = getSelectedOption(malicious_selector);
  } else {
      var label = 'benign';
      var family = getSelectedOption(benign_selector);
  }
  return [label, family];
}

function getSelectedFamilies() {
  var label_family = getSelectedFamily();
  var label = label_family[0];
  var families = label_family[1];
  families = families.join();
  return [label, families];
}

function displayRename(modif_div) {

  function renameCallback() {
    var label_family = getSelectedFamily();
    var selected_label  = label_family[0];
    var selected_family = label_family[1];
    var new_family_name = $('#rename_field').val();
    var query = buildQuery('changeFamilyName',
                           [exp_id,
                            conf.annotations_conf.annotations_id,
                            selected_label, selected_family,
                            new_family_name]);
    $.ajax({url: query, async: false});
    displayRename(modif_div);
    updateFamiliesStats();
  }

  cleanDiv(modif_div.id);
  var panel = createPanel('panel-primary', 'row', 'Rename a Family', modif_div);
  displayFamiliesSelectors(panel);

  // Label
  var label_group = createDivWithClass('', 'form_group row', panel);
  var label_label = document.createElement('label');
  label_label.setAttribute('class', 'col-md-4 control-label');
  label_label.appendChild(document.createTextNode('New Family Name'));
  label_group.appendChild(label_label);

  var input_group = createDivWithClass(null, 'input-group', panel);
  // Input field
  var rename_field = document.createElement('input');
  rename_field.setAttribute('class', 'form-control');
  rename_field.setAttribute('type', 'text');
  rename_field.setAttribute('id', 'rename_field');
  rename_field.setAttribute('size', 5);
  input_group.appendChild(rename_field);
  // Button
  var button_span = document.createElement('span');
  button_span.setAttribute('class', 'input-group-btn');
  input_group.appendChild(button_span);
  var rename_button = document.createElement('button');
  rename_button.id = 'rename_button';
  rename_button.setAttribute('class', 'btn btn-primary');
  rename_button.setAttribute('type', 'button');
  var text = document.createTextNode('Rename');
  rename_button.appendChild(text);
  rename_button.addEventListener('click', renameCallback);
  button_span.appendChild(rename_button);
}

function displayChange(modif_div) {

  function changeLabelCallback() {
    var label_family    = getSelectedFamily();
    var selected_label  = label_family[0];
    var selected_family = label_family[1];
    var query = buildQuery('changeFamilyLabel',
                           [exp_id,
                            conf.annotations_conf.annotations_id,
                            selected_label, selected_family]);
    $.ajax({url: query, async: false});
    displayChange(modif_div);
    updateFamiliesStats();
  }

  cleanDiv(modif_div.id);
  var panel = createPanel('panel-primary', 'row',
                          'Swap Malicious/Benign for a Family', modif_div);
  displayFamiliesSelectors(panel);
  // Button
  var input_group = createDivWithClass(null, 'input-group', panel);
  var button_span = document.createElement('span');
  button_span.setAttribute('class', 'input-group-btn');
  input_group.appendChild(button_span);
  var change_button = document.createElement('button');
  change_button.id = 'change_button';
  change_button.setAttribute('class', 'btn btn-primary');
  change_button.setAttribute('type', 'button');
  var text = document.createTextNode('Swap Malicious/Benign');
  change_button.appendChild(text);
  change_button.addEventListener('click', changeLabelCallback);
  button_span.appendChild(change_button);
}

function displayMerge(modif_div) {

  function mergeCallback() {
    var label_family      = getSelectedFamilies();
    var selected_label    = label_family[0];
    var selected_families = label_family[1];
    var new_family_name   = $('#merge_field').val();
    var query = buildQuery('mergeFamilies',
                           [exp_id,
                            conf.annotations_conf.annotations_id,
                            selected_label, selected_families,
                            new_family_name]);
    $.ajax({url: query, async: false});
    displayMerge(modif_div);
    updateFamiliesStats();
  }

  cleanDiv(modif_div.id);
  var panel = createPanel('panel-primary', 'row', 'Merge Several Families',
                          modif_div);
  displayFamiliesSelectors(panel, multiple = true);

  // Label
  var label_group = createDivWithClass('', 'form_group row', panel);
  var label_label = document.createElement('label');
  label_label.setAttribute('class', 'col-md-4 control-label');
  label_label.appendChild(document.createTextNode('New Family Name'));
  label_group.appendChild(label_label);

  var input_group = createDivWithClass(null, 'input-group', panel);
  // Input field
  var merge_field = document.createElement('input');
  merge_field.setAttribute('class', 'form-control');
  merge_field.setAttribute('type', 'text');
  merge_field.setAttribute('id', 'merge_field');
  merge_field.setAttribute('size', 5);
  input_group.appendChild(merge_field);
  // Button
  var button_span = document.createElement('span');
  button_span.setAttribute('class', 'input-group-btn');
  input_group.appendChild(button_span);
  var merge_button = document.createElement('button');
  merge_button.id = 'merge_button';
  merge_button.setAttribute('class', 'btn btn-primary');
  merge_button.setAttribute('type', 'button');
  var text = document.createTextNode('Merge');
  merge_button.appendChild(text);
  merge_button.addEventListener('click', mergeCallback);
  button_span.appendChild(merge_button);
}

function displayEdit(button_id) {
  return function() {
    var modif_div = cleanDiv('modif_div');
    if (button_id == 'rename') {
        displayRename(modif_div);
    } else if (button_id == 'change') {
        displayChange(modif_div);
    } else if (button_id == 'merge') {
        displayMerge(modif_div);
    }
  }
}

function updateFamiliesStats(label=null) {
  if (!label) {
    updateFamiliesStats('malicious');
    updateFamiliesStats('benign');
    return;
  }
  var stats_panel = cleanDiv('stats_panel_' + label);
  var query = buildQuery('getFamiliesBarplot', [annotations_id, 'None', label]);
  $.getJSON(query, function (data) {
      var options = barPlotOptions(data, 'Families');
      var barPlot = drawBarPlot(stats_panel.id,
                                options, data,
                                type='bar', width='750px', height='300px',
                                callback=null);
  });
}

function displayAvailableActions(edit_panel) {
  var select_actions_col = createPanel('panel-primary', 'col-md-3',
                                       'Select an Action', edit_panel);

  var list_group = createDivWithClass(null, 'list-group',
                                      parent_div=select_actions_col);
  var rename = document.createElement('a');
  rename.setAttribute('class', 'list-group-item');
  rename.appendChild(document.createTextNode('Rename'));
  rename.addEventListener('click', displayEdit('rename'));
  list_group.appendChild(rename);

  var change = document.createElement('a');
  change.setAttribute('class', 'list-group-item');
  change.appendChild(document.createTextNode('Swap Malicious/Benign'));
  change.addEventListener('click', displayEdit('change'));
  list_group.appendChild(change);

  var merge = document.createElement('a');
  merge.setAttribute('class', 'list-group-item');
  merge.appendChild(document.createTextNode('Merge'));
  merge.addEventListener('click', displayEdit('merge'));
  list_group.appendChild(merge);

  var modif_div = createDivWithClass('modif_div', 'col-md-9',
                                     parent_div=edit_panel);
}

function displayDivisions() {
  var main = $('#main')[0];

  // Editing Families
  var edit_row = createDivWithClass(null, 'row', parent_div = main);
  var edit_panel = createPanel('panel-primary', 'col-md-8', 'Family Editor',
                               edit_row);
  displayAvailableActions(edit_panel);

  // Families Statistics
  var stats_row = createDivWithClass(null, 'row', parent_div = main);
  var stats_panel = createPanel('panel-primary', 'col-md-12',
                                'Number of Instances per Family', stats_row);
  var stats_panel_m = createPanel('panel-danger', 'col-md-6',
                                  'Malicious Families', stats_panel);
  stats_panel_m.setAttribute('id', 'stats_panel_malicious');
  var stats_panel_b = createPanel('panel-success', 'col-md-6',
                                  'Benign Families', stats_panel);
  stats_panel_b.setAttribute('id', 'stats_panel_benign');
  updateFamiliesStats();
}
