function setInstancesSettings(train_test, project, dataset, experiment_id, experiment_label_id,
        callback) {
    if (train_test == 'validation') {
      var query = buildQuery('getActiveLearningValidationConf', 
                      [project, dataset, experiment_id]);
      $.getJSON(query, function(data) {
        inst_dataset      = data['test_dataset'].split('__')[0];
        inst_exp_id       = data['test_exp']['experiment_id'];
        inst_exp_label_id = data['test_exp']['experiment_label_id'];
        callback();
      });
    } else {
      var query = buildQuery('getSupervisedValidationConf', 
                      [project, dataset, experiment_id]);
      $.getJSON(query, function(data) {
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
    function callback() {
        printInstanceData(selected_instance_id, selected_instance_ident);
    }
    var div_name = 'instance_data';
    var div_object = $('#' + div_name)[0];
    var radio_div = createDiv('radio_div');
    var radio_list = [['features', 'Features', false]];
    if (conf.kind == 'SupervisedLearning') {
        var supervised_radio_list = [
                  ['weighted_features', 'Weighted Features', false]];
        radio_list.push.apply(radio_list, supervised_radio_list);
    }
    try {
        specificInformationStructure(radio_list);
    } catch(err) {
        console.log(
              'TODO: specific function to print information about an instance');
    }
    if (!radio_list.map(function(index,e){index[2]}).some(Boolean)) {
        radio_list[0][2] = true;
    }
    for (var i = 0, len = radio_list.length; i < len; i++) {
        var t_radio = makeRadioButton('radio_instance', ...radio_list[i], callback);
        radio_div.appendChild(t_radio);
    }
    div_object.appendChild(radio_div);
    var instance_data_div = createDiv('instance_data_div');
    div_object.appendChild(instance_data_div);
}

function printInstanceInformation(selected_id, predicted_proba = false) {
  cleanInstanceInformation();
  selected_instance_proba = predicted_proba;
  //Instance label
  selected_instance_ident = printInstanceLabel(selected_id);
  // Instance data
  printInstanceData(selected_id, selected_instance_ident);
}
function printInstanceData(selected_id, ident) {
  // Instance data
  var selected_radio = $('input[name=\'radio_instance\']:checked').val()
  switch (selected_radio) {
      case 'features':
          printFeatures(selected_id);
          break;
      case 'weighted_features':
          printWeightedFeatures(selected_id);
          break;
      default:
          try {
              printSpecificData(selected_id, selected_instance_ident, selected_radio);
          } catch(err) {
            console.log(
              'TODO: specific function to print information about an instance');
          }
  }
}

function cleanInstanceInformation() {
  try {
    cleanInformation();
  } catch (err) {
    console.log(
      'TODO: specific function to print information about an instance');
  }
  cleanDiv('instance_ident');
}

// Label
function printInstanceLabel(selected_id) {
    var ident_div = cleanDiv('instance_ident');
    // Ident
    var xmlHttp = new XMLHttpRequest();
    var query = buildQuery('getIdent',
                    [project, inst_dataset, selected_id])
    xmlHttp.open('GET', query, false); 
    xmlHttp.send(null);
    var ident = xmlHttp.responseText;
    if (hide_confidential) {
      var ident_node = document.createTextNode('');
    } else {
      var ident_node = document.createTextNode(ident);
    }
    $('#instance_ident')[0].appendChild(ident_node);
    // Label
    var query = buildQuery('getLabel',
                    [project, inst_dataset, inst_exp_label_id, selected_id]);
    $.getJSON(query, function(data) {
        displayLabel($('#instance_label')[0], data);
    });
    return ident;
}

function addSublabelCallback(label) {
    var prefix = 'instance_';
    return function() {
        // Add sublabel to the select list
        var select = $('#' + prefix + label + '_sublabel_selector')[0];
        var new_sublabel = $('#' + prefix + label + '_add_sublabel_field').val();
        if (new_sublabel != '') {
            addElementToSelectList(select, new_sublabel, selected = true);
        } else {
            alert('Cannot add an empty sublabel.');
            return;
        }
        $('#' + prefix + label + '_add_sublabel_field')[0].value = '';
        // Add the label
        addLabelCallback(label, project, inst_dataset, 
                inst_exp_label_id, label_iteration,
                label_method)();
    }
}

function displaySublabelSelector(label_row, label, cluster = false) {
  var prefix = 'instance_';
  if (cluster) {
    prefix = 'cluster_';
  }
  var col = createDivWithClass('None', 'col-md-5',
          parent_div = label_row);
  // Selection
  var select = $('#' + prefix + label + '_sublabel_selector')[0];
  createSelectList(prefix + label + '_sublabel_selector', 5, null, parent_div = col);
  var select = $('#' + prefix + label + '_sublabel_selector')[0];
  // Adding value input
  if (!cluster) {
    var row = createDivWithClass('None', 'row', parent_div = col);
    var add_sublabel_field = document.createElement('input');
    add_sublabel_field.setAttribute('id', prefix + label + '_add_sublabel_field');
    add_sublabel_field.setAttribute('size', 10);
    row.appendChild(add_sublabel_field);
    add_sublabel_button = document.createElement('button');
    add_sublabel_button.id = prefix + 'add_sublabel_button';
    var text = document.createTextNode('Add');
    add_sublabel_button.appendChild(text);
    add_sublabel_button.addEventListener('click', addSublabelCallback(label));
    row.appendChild(add_sublabel_button);
  }
  // Sublabel values
  var query = buildQuery('getLabelsSublabels', [project, inst_dataset, inst_exp_label_id]);
  $.getJSON(query, function(data) {
      var select = $('#' + prefix + label + '_sublabel_selector')[0];
      if (data[label]) {
        var sublabels = Object.keys(data[label]);
        sublabels.forEach(function(q) {
            addElementToSelectList(select, q);
        });
      } else {
          // When there is no sublabel, the default sublabel, 'other' is proposed
          addElementToSelectList(select, 'other');

      }
  });
  return col;
}

function displayAnnotationDiv() {
  var label_div = cleanDiv('instance_label');
  addTitle(label_div, 'Instance Label');
  // Remove button
  var remove_row = createDivWithClass('None', 'row',
          parent_div = label_div);
  var button = document.createElement('button');
  var button_text = document.createTextNode('Remove');
  button.appendChild(button_text);
  button.addEventListener('click', removeLabelCallback(
              project, inst_dataset, inst_exp_label_id));
  remove_row.appendChild(button);
  var label_row = createDivWithClass('None', 'row',
          parent_div = label_div);
  // Sublabels
  var malicious_col = displaySublabelSelector(label_row, 'malicious');
  var benign_col    = displaySublabelSelector(label_row, 'benign');
  // Label buttons
  // Benign Button
  benign_label = 'ok';
  var benign_button =  document.createElement('button');
  benign_button.id = 'benign_button';
  var benign_text = document.createTextNode(benign_label);
  benign_button.appendChild(benign_text);
  benign_button.addEventListener('click', addLabelCallback(
              'benign', project, inst_dataset, 
              inst_exp_label_id, label_iteration,
              label_method));
  benign_col.appendChild(benign_button);
  // Malicious Button
  malicious_label = 'alert';
  var malicious_button = document.createElement('button');
  malicious_button.id = 'malicious_button';
  var malicious_text = document.createTextNode(malicious_label);
  malicious_button.appendChild(malicious_text);
  malicious_button.addEventListener('click', addLabelCallback(
              'malicious', project, inst_dataset, 
              inst_exp_label_id, label_iteration,
              label_method));
  malicious_col.appendChild(malicious_button);
}

function displayLabel(label_div, label_sublabel, cluster = false) {
  var prefix = 'instance_';
  if (cluster) {
    prefix = 'cluster_';
  }
  if (Object.keys(label_sublabel).length == 2) {
    var label = label_sublabel.label;
    var sublabel = label_sublabel.sublabel;
    if (label == 'malicious') {
      $('#malicious_button')[0].style.background = 'red';
      $('#benign_button')[0].style.background = null;
      $('#' + prefix + 'malicious_sublabel_selector')[0].value = sublabel;
      $('#' + prefix + 'benign_sublabel_selector')[0].selectedIndex = -1;
    } else if (label == 'benign') {
      $('#benign_button')[0].style.background = 'green';
      $('#malicious_button')[0].style.background = null;
      $('#' + prefix + 'benign_sublabel_selector')[0].value = sublabel;
      $('#' + prefix + 'malicious_sublabel_selector')[0].selectedIndex = -1;
    }
  } else {
    var labels = ['malicious', 'benign'];
    for (var l in labels) {
      var label = labels[l];
      $('#' + prefix + label + '_sublabel_selector')[0].value = last_sublabel[label];
      $('#' + label + '_button')[0].style.background = null;
    }
  }
}

function setLastSublabel(label, sublabel) {
    last_sublabel[label] = sublabel;
    // If clustering - change selected sublabel
    var cluster_selector = $('#cluster_' + label + '_sublabel_selector')[0]
    if (cluster_selector) {
        cluster_selector.value = sublabel;
    }
}

function addLabelCallback(label, project, inst_dataset, inst_exp_label_id,
        label_iteration, label_method) {
  return function() {
    var sublabel = $('#instance_' + label + '_sublabel_selector').val();
    if (!sublabel) {
        alert('A sublabel must be selected.');
        return;
    }
    var instance_id = getSelectedOption(last_instance_selector);
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
                      label, sublabel,
                      label_method, true]);
      $.ajax({url: query});
      // Update instance visu
      if (label == 'malicious') {
        $('#malicious_button')[0].style.background = 'red';
        $('#benign_button')[0].style.background = null;
      } else if (label == 'benign') {
        $('#benign_button')[0].style.background = 'green';
        $('#malicious_button')[0].style.background = null;
      }
      last_instance_selector.focus();
      setLastSublabel(label, sublabel);
    }
  };
}

function removeLabelCallback(project, inst_dataset, inst_exp_label_id) {
  return function() {
    var instance_id = getSelectedOption(last_instance_selector);
    var query = buildQuery('removeLabel',
                    [project, inst_dataset, inst_exp_label_id, 
                    instance_id]);
    $.ajax({url: query});
    $('#benign_button')[0].style.background = null;
    $('#malicious_button')[0].style.background = null;
    last_instance_selector.focus();
  }
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
    selected_instance_id = getSelectedOption(instances_selector);
    printInstanceInformation(selected_instance_id);
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

// Instances Data

function printFeatures(selected_id) {
    var div_object = cleanDiv('instance_data_div');
    var title = document.createElement('h5');
    title.innerHTML = 'Instance ID : ' + selected_id;
    div_object.appendChild(title);
    var query = buildQuery('getFeatures',
                [project, dataset, inst_exp_id, inst_dataset, selected_id]);
    $.getJSON(query, function(data) {
        var ul = document.createElement('ul');
        for (var key in data) {
            var li = document.createElement('li');
            li.appendChild(document.createTextNode(
                            data[key][0] + ' : ' + data[key][1]));
            ul.appendChild(li);
        }
        div_object.appendChild(ul);
    });
}


function printWeightedFeatures(selected_id) {
    var div_object = cleanDiv('instance_data_div');
    var proba = document.createElement('h5');
    proba.innerHTML = 'Predicted proba : ' + selected_instance_proba;
    div_object.appendChild(proba);
    var graph_div  = createDiv('instance_graph_div', div_object);
    //first we get the Weighted Bar plot json for the plot
    var query = buildQuery('getTopWeightedFeatures',
                [project, dataset, experiment_id, inst_dataset, inst_exp_id, selected_id, 20]);
    $.getJSON(query, function(data) {
        var weighted_features = data;
        var weighted_data = {labels:[],
                             datasets:[{data:[],
                                        backgroundColor:'red',
                                        label:selected_id}]
                            };
        var data_labels = [];
        for (var key in weighted_features) {
            weighted_data.labels.push(weighted_features[key][0]);
            weighted_data.datasets[0].data.push(weighted_features[key][2]);
            data_labels.push(weighted_features[key][1]);
        }
        //then we plot
        var options = barPlotOptions(weighted_data, data_labels);
        var barPlot = drawBarPlot('instance_graph_div', options,
                                  weighted_data, 'horizontalBar');
        graph_div.style.width = '800px';
        graph_div.style.height = '500px';
    });
}
