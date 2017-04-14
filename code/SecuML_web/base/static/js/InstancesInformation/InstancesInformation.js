var num_coeff = 15;

// Annotation and Description panels
function displayInstancePanel(parent_div) {
  var instance_panel = createPanel('panel-primary', 'col-md-12', 'Instance', parent_div,
          return_heading = true);
  var instance = instance_panel[0];
  var instance_title = instance_panel[1];
  instance_title.setAttribute('id', 'instance_title');
  var annotation = createPanel('panel-primary', 'col-md-5', 'Annotation', instance);
  annotation.setAttribute('id', 'instance_label');
  var description = createDivWithClass(null, 'col-md-7', instance);
  var instance_panel = createPanel('panel-primary', 'col-md-12', 'Description', description);
  var instance_proba = createDivWithClass('instance_predicted_proba', 'row', instance_panel);
  var instance_data = createDivWithClass('instance_data', 'row', instance_panel);
}

function setInstancesSettings(train_test, project, dataset, experiment_id, experiment_label_id,
        callback) {
    if (train_test == 'validation') {
      var query = buildQuery('getActiveLearningValidationConf',
                      [project, dataset, experiment_id]);
      jQuery.getJSON(query, function(data) {
        inst_dataset      = data['test_dataset'].split('__')[0];
        inst_exp_id       = data['test_exp']['experiment_id'];
        inst_exp_label_id = data['test_exp']['experiment_label_id'];
        callback();
      });
    } else if (train_test == 'train') {
      inst_dataset = dataset;
      inst_exp_id = experiment_id;
      inst_exp_label_id = experiment_label_id;
      callback();
    } else {
      var query = buildQuery('getSupervisedValidationConf',
                      [project, dataset, experiment_id]);
      jQuery.getJSON(query, function(data) {
        if (data['method'] == 'random_split' || data['method'] == 'unlabeled') {
            inst_dataset = dataset;
            inst_exp_id = experiment_id;
            inst_exp_label_id = experiment_label_id;
        } else {
            inst_dataset      = data['test_dataset'].split('__')[0];
            inst_exp_id       = data['test_exp']['experiment_id'];
            inst_exp_label_id = data['test_exp']['experiment_label_id'];
        }
        callback();
      });
    }
}

function displayInstanceInformationStructure() {
    var tabs_div = document.getElementById('instance_data');
    var menu_titles = ['Features'];
    var menu_labels = ['features'];
    if (conf.kind == 'Classification') {
        if (conf.classification_conf.feature_coefficients) {
          menu_titles.push('Weighted Features');
          menu_labels.push('weighted_features');
        }
    }
    try {
        specific_tabs = specificTabs();
        menu_titles.unshift(specific_tabs[0]);
        menu_labels.unshift(specific_tabs[1]);
    } catch(err) {
        console.log('TODO: specific function to print information about an instance');
    }
    var menu = createTabsMenu(menu_labels, menu_titles, tabs_div, 'instance_tabs');
}

function printInstanceInformation(selected_id, suggested_label = null, suggested_family = null) {
  cleanInstanceInformation();
  var ident = printInstanceIndent(selected_id);
  printInstanceLabel(selected_id, suggested_label, suggested_family);
  printInstanceData(selected_id, ident);
}

function printInstanceData(selected_id, ident) {
  printFeatures(selected_id);
  if (conf.kind == 'Classification') {
    printWeightedFeatures(selected_id);
  }
  try {
      printSpecificInformations(selected_id, ident);
  } catch(err) {
      return;
  }
}

function cleanInstanceInformation() {
  try {
    cleanInformation();
  } catch (err) {
    console.log(
      'TODO: specific function to print information about an instance');
  }
}

function printInstanceIndent(selected_id) {
    var query = buildQuery('getIdent',
                    [project, inst_dataset, selected_id]);
    var ident = $.ajax({url: query, async: false}).responseText;
    document.getElementById('instance_title').textContent = 'Instance ' + selected_id + ': ' + ident;
    return ident;
}

function printInstanceLabel(selected_id, suggested_label, suggested_family) {
    var query = buildQuery('getLabel',
                    [project, inst_dataset, inst_exp_label_id, selected_id]);
    jQuery.getJSON(query, function(data){
      var prefix = 'instance_';
      var label_value = cleanDiv('instance_' + 'label_value');
      if (Object.keys(data).length == 2) {
        var label = data.label;
        var family = data.family;
        if (label == 'malicious') {
          label_value.setAttribute('class', 'label label-danger');
        } else {
          label_value.setAttribute('class', 'label label-success');
        }
        label_value.appendChild(document.createTextNode(upperCaseFirst(label)));
        var other_label = otherLabel(label);
        $('#' + prefix + label + '_family_selector')[0].value = family;
        $('#' + prefix + other_label + '_family_selector')[0].selectedIndex = -1;
      } else {
        label_value.setAttribute('class', 'label label-default');
        $('#' + prefix + 'malicious_family_selector')[0].selectedIndex = -1;
        $('#' + prefix + 'benign_family_selector')[0].selectedIndex = -1;
        if (suggested_label && suggested_family) {
          $('#' + prefix + suggested_label + '_family_selector')[0].value = suggested_family;
          label_value.appendChild(document.createTextNode(upperCaseFirst(suggested_label)));
        } else {
          label_value.appendChild(document.createTextNode('None'));
        }
      }
      var suggestion_value = cleanDiv('suggested_family');
      if (suggestion_value) {
          if (suggested_label && suggested_family) {
              if (suggested_label == 'benign') {
                suggestion_value.setAttribute('class', 'label label-success');
              } else {
                suggestion_value.setAttribute('class', 'label label-danger');
              }
              suggestion_value.appendChild(document.createTextNode(suggested_family));
          } else {
              var suggestion_value = cleanDiv('suggested_family');
              suggestion_value.setAttribute('class', 'label label-default');
              suggestion_value.appendChild(document.createTextNode('None'));
          }
      }
    });
}

function addFamilyCallback(label) {
    var prefix = 'instance_';
    return function() {
        var select = $('#' + prefix + label + '_family_selector')[0];
        var new_family = $('#' + prefix + label + '_add_family_field').val();
        // Check not already in the select list
        for (var i = 0, n = select.options.length; i < n; i++) {
          if (select.options[i].text == new_family) {
              alert('This family already exists.');
              return;
          }
        }
        if (new_family != '') {
            addElementToSelectList(select, new_family, selected = true);
            familyChangeCallback(label)();
            $('#' + prefix + label + '_add_family_field')[0].value = '';
        } else {
            alert('Cannot add an empty family.');
        }
    }
}

function displayFamilySelector(label_row, label, cluster = false) {
  var prefix = 'instance_';
  if (cluster) {
    prefix = 'cluster_';
  }
  var col = createDivWithClass(null, 'col-lg-6', parent_div = label_row);
  // Selection
  var select = $('#' + prefix + label + '_family_selector')[0];
  var label_title = label.charAt(0).toUpperCase() + label.substr(1) + ' Families';
  var selector_size = 6;
  if (cluster) {
      selector_size = 5;
  }
  createSelectList(prefix + label + '_family_selector', selector_size, null, col, label_title);

  var select = $('#' + prefix + label + '_family_selector')[0];
  // Adding value input
  if (!cluster) {
    var input_group = createDivWithClass(null, 'input-group', col);
    // Input field
    var add_family_field = document.createElement('input');
    add_family_field.setAttribute('class', 'form-control');
    add_family_field.setAttribute('type', 'text');
    add_family_field.setAttribute('id', prefix + label + '_add_family_field');
    add_family_field.setAttribute('size', 5);
    input_group.appendChild(add_family_field);
    // Button
    var button_span = document.createElement('span');
    button_span.setAttribute('class', 'input-group-btn');
    input_group.appendChild(button_span);
    var add_family_button = document.createElement('button');
    add_family_button.id = prefix + 'add_family_button';
    add_family_button.setAttribute('class', 'btn btn-default');
    add_family_button.setAttribute('type', 'button');
    var text = document.createTextNode('Add');
    add_family_button.appendChild(text);
    add_family_button.addEventListener('click', addFamilyCallback(label));
    button_span.appendChild(add_family_button);
  }
  // Family values
  var query = buildQuery('getLabelsFamilies', [project, inst_dataset, inst_exp_label_id]);
  jQuery.getJSON(query, function(data) {
      var select = $('#' + prefix + label + '_family_selector')[0];
      if (data[label]) {
        var families = Object.keys(data[label]);
        families.forEach(function(q) {
            addElementToSelectList(select, q);
        });
      } else {
          // When there is no family, the default family, 'other' is proposed
          addElementToSelectList(select, 'other');

      }
  });
  // Add family selector callback
  select.addEventListener('change', familyChangeCallback(label, cluster));
  return col;
}

function familyChangeCallback(selected_label, cluster = false) {
    return function() {
      var prefix = 'instance_';
      if (cluster) {
        prefix = 'cluster_';
      }
      // Unselect the family of the other label
      var other_label = otherLabel(selected_label);
      var other_selector = $('#' + prefix + other_label + '_family_selector')[0];
      other_selector.selectedIndex = -1;
      // Change the label
      var label_value = cleanDiv(prefix + 'label_value');
      label_value.setAttribute('class', 'label label-default');
      label_value.appendChild(document.createTextNode(upperCaseFirst(selected_label)));
    }
}

function displayAnnotationDiv(suggestion = false) {
  var prefix = 'instance_';
  var label_div = cleanDiv('instance_label');
  var form = document.createElement('form');
  form.setAttribute('class', 'form-horizontal');
  label_div.appendChild(form);
  var fieldset = document.createElement('fieldset');
  form.appendChild(fieldset);

  // Label
  if (suggestion) {
     var suggestion_group = createDivWithClass('', 'form_group row', fieldset);
     var suggestion_label = document.createElement('label');
     suggestion_label.setAttribute('class', 'col-lg-3 control-label');
     suggestion_label.appendChild(document.createTextNode('Suggestion'));
     suggestion_group.appendChild(suggestion_label);
     var suggestion_value_header = document.createElement('h4');
     suggestion_group.appendChild(suggestion_value_header);
     var suggestion_value = document.createElement('label');
     suggestion_value.setAttribute('class', 'label label-default');
     suggestion_value.setAttribute('id', 'suggested_family');
     suggestion_value.appendChild(document.createTextNode('None'));
     suggestion_value_header.appendChild(suggestion_value);
  }

  // Families
  var malicious_col = displayFamilySelector(fieldset, 'malicious');
  var benign_col    = displayFamilySelector(fieldset, 'benign');

  // Label
  var label_group = createDivWithClass('', 'form_group row', fieldset);
  var label_label = document.createElement('label');
  label_label.setAttribute('class', 'col-lg-2 control-label');
  label_label.appendChild(document.createTextNode('Label'));
  label_group.appendChild(label_label);
  var label_value_header = document.createElement('h4');
  label_group.appendChild(label_value_header);
  var label_value = document.createElement('label');
  label_value.setAttribute('class', 'label label-default');
  label_value.setAttribute('id', prefix + 'label_value');
  label_value.appendChild(document.createTextNode(''));
  label_value_header.appendChild(label_value);

  // Ok and Remove button
  var ok_remove_group = createDivWithClass('', 'form-group row', fieldset);
  /// Ok button
  var ok_div = createDivWithClass(null, 'col-lg-2', ok_remove_group);
  var ok_button = document.createElement('button');
  ok_button.setAttribute('class', 'btn btn-primary');
  ok_button.setAttribute('type', 'button');
  ok_button.setAttribute('id', 'ok_button');
  var ok_button_text = document.createTextNode('Ok');
  ok_button.appendChild(ok_button_text);
  ok_button.addEventListener('click', addLabelCallback(project, inst_dataset, inst_exp_label_id,
              label_iteration));
  ok_div.appendChild(ok_button);
  /// Remove button
  var remove_div = createDivWithClass(null, 'col-lg-2 col-lg-offset-1', ok_remove_group);
  var button = document.createElement('button');
  button.setAttribute('class', 'btn btn-default');
  button.setAttribute('type', 'button');
  var button_text = document.createTextNode('Remove');
  button.appendChild(button_text);
  button.addEventListener('click', removeLabelCallback(
            project, inst_dataset, inst_exp_label_id));
  remove_div.appendChild(button);
}

function getCurrentAnnotation(prefix) {
  var label = '';
  var family = '';
  var malicious_selector = $('#' + prefix + '_malicious_family_selector')[0];
  var benign_selector    = $('#' + prefix + '_benign_family_selector')[0];
  if (malicious_selector.selectedIndex != -1) {
      label = 'malicious';
      family = getSelectedOption(malicious_selector);
  } else {
      label = 'benign';
      family = getSelectedOption(benign_selector);
  }
  return [label, family];
}

function addLabelCallback(project, inst_dataset, inst_exp_label_id, label_iteration) {
  return function() {
    var instance_id     = getCurrentInstance();
    var [label, family] = getCurrentAnnotation('instance');
    if (!family) {
        alert('A family must be selected.');
        return;
    }
    if (instance_id) {
      // Remove previous label
      var query = buildQuery('removeLabel',
                      [project, inst_dataset, inst_exp_label_id,
                      instance_id]);
      $.ajax({url: query});
      // Add new label
      var query = buildQuery('addLabel',
                      [project, inst_dataset, inst_exp_label_id,
                      label_iteration,
                      instance_id,
                      label, family,
                      label_method, true]);
      $.ajax({url: query,
              success: function(data) {
                printInstanceLabel(instance_id);
              }});
      document.getElementById('next_button').focus();
    }
  };
}

function removeLabelCallback(project, inst_dataset, inst_exp_label_id) {
  return function() {
    var instance_id = getCurrentInstance();
    //var instance_id = instances_list[current_instance_index];
    var query = buildQuery('removeLabel',
                    [project, inst_dataset, inst_exp_label_id,
                    instance_id]);
    $.ajax({url: query,
            success: function(data) {
              printInstanceLabel(instance_id);
            }});
  }
}

function printFeatures(selected_id) {
    var div_object = cleanDiv('features');
    var query = buildQuery('getFeatures',
                [project, dataset, inst_exp_id, inst_dataset, selected_id]);
    jQuery.getJSON(query, function(data) {
        var ul = document.createElement('ul');
        for (var key in data) {
            var li = document.createElement('li');
            li.appendChild(document.createTextNode(
                            key + ' : ' + data[key]));
            ul.appendChild(li);
        }
        div_object.appendChild(ul);
    });
}

function printWeightedFeatures(selected_id) {
    var div_object = cleanDiv('weighted_features');
    var graph_div  = createDiv('instance_graph_div', div_object);
    var query = buildQuery('getTopWeightedFeatures',
                [project, dataset, experiment_id, inst_dataset, inst_exp_id, selected_id, num_coeff]);
    jQuery.getJSON(query, function(data) {
        var tooltip_data = data.datasets[0].tooltip_data
        var options = barPlotOptions(data, tooltip_data);
        options.legend.display = false;
        var barPlot = drawBarPlot('instance_graph_div', options,
                                  data, 'horizontalBar');
        graph_div.style.width = '800px';
        graph_div.style.height = '500px';
    });
}

// Instances Lists
function displayInstancesList(malicious_ok, instances) {
  clearInstancesList(malicious_ok);
  if (instances.length == 0)
      return;
  var instance_selector = $('#instances_selector_' + malicious_ok)[0];
  for (var i in instances) {
    var opt = document.createElement('option');
    opt.text = instances[i];
    instance_selector.add(opt);
  }
}

function createInstancesSelector(malicious_ok) {
  var instances_selector = $('#instances_selector_' + malicious_ok)[0];
  instances_selector.addEventListener('change', function() {
    selected_id = getSelectedOption(instances_selector);
    printInstanceInformation(selected_id);
    last_instance_selector = this;
  }, false);
}

function createInstancesSelectors() {
  createInstancesSelector('ok');
  createInstancesSelector('malicious');
}

function clearInstancesList(malicious_ok) {
    cleanDiv('instances_selector_' + malicious_ok);
}

function clearInstancesLists() {
    clearInstancesList('malicious');
    clearInstancesList('ok');
}
