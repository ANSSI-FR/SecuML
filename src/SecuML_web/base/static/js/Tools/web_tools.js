function upperCaseFirst(str) {
  return str.charAt(0).toUpperCase() + str.substring(1);
}

function buildQuery(name, args) {
  query  = '/' + name + '/';
  query += args.join('/') + '/';
  return query;
}

function addTitle(div, title) {
  var h = document.createElement('h4');
  h.textContent = title;
  div.appendChild(h);
}

function createDiv(id, parent_div = null, title = null) {
    var div = document.createElement('div');
    div.setAttribute('id', id);
    if (parent_div) {
      parent_div.appendChild(div);
    }
    if (title) {
      addTitle(div, title);
    }
    return div;
}

function createDivWithClass(id, classname, parent_div = null, title = null) {
    var div = createDiv(id, parent_div = parent_div, title = title);
    div.setAttribute('class', classname);
    return div;
}

function createPanel(panel_type, col_size, heading, parent_div, return_heading = false) {
  if (col_size) {
    var col = createDivWithClass(null, col_size, parent_div);
    parent_div = col;
  }
  var panel = createDivWithClass(null,
          'panel ' + panel_type,
          parent_div = parent_div);
  if (heading) {
    var panel_heading = createDivWithClass(null, 'panel-heading',
            parent_div = panel);
    if (typeof heading == 'string') {
      var panel_title = document.createElement('h3');
      panel_title.setAttribute('class', 'panel-title');
      panel_title.textContent = heading;
      panel_heading.appendChild(panel_title);
    } else {
      panel_heading.appendChild(heading);
    }
  }
  var panel_body = createDivWithClass(null, 'panel-body',
          parent_div = panel);
  if (return_heading) {
    return [panel_body, panel_title];
  } else {
    return panel_body;
  }
}

function createCollapsingPanel(panel_type, col_size, heading, parent_div, collapse_id) {
  if (col_size) {
    var col = createDivWithClass(null, col_size, parent_div);
    parent_div = col;
  }
  var panel_group = createDivWithClass(null, 'panel_group', parent_div);

  var panel = createDivWithClass(null,
          'panel ' + panel_type,
          parent_div = panel_group);

  var title_link = document.createElement('a');
  title_link.setAttribute('data-toggle', 'collapse');
  title_link.appendChild(document.createTextNode(heading));
  title_link.href = '#' + collapse_id + '_collapse';

  var panel_heading = createDivWithClass(null, 'panel-heading',
          parent_div = panel);
  var panel_title = document.createElement('h3');
  panel_title.setAttribute('class', 'panel-title');
  panel_title.appendChild(title_link);
  panel_heading.appendChild(panel_title);

  var panel_collapse = createDivWithClass(collapse_id + '_collapse', 'panel-collapse collapse', panel);
  var panel_body = createDivWithClass(collapse_id, 'panel-body', panel_collapse);
  return panel_body;
}

function createTable(div_name, titles, table_id = null, width = null) {
  var items = $('#' + div_name)[0];
  var table = document.createElement('table');
  table.setAttribute('class', 'table table-striped table-hover');
  if (width) {
    table.setAttribute('style', width);
  }
  if (titles) {
    var header = document.createElement('thead');
    var tr = document.createElement('tr');
    header.appendChild(tr);
    for (var i in titles) {
      var th = document.createElement('th');
      th.innerHTML = titles[i];
      tr.appendChild(th);
    }
    table.appendChild(header);
  }
  var body = document.createElement('tbody');
  if (table_id) {
    body.setAttribute('id', table_id);
  }
  table.appendChild(body);
  items.appendChild(table);
  return body;
}

function addRow(body, elements, title = false, row_class = null) {
  var tr = document.createElement('tr');
  if (row_class) {
    tr.setAttribute('class', row_class);
  }
  for (var i in elements) {
    var td = document.createElement('td');
    if (i == 0 && title) {
      td = document.createElement('th');
    }
    td.innerHTML = elements[i];
    tr.appendChild(td);
  }
  body.appendChild(tr);
}

function createTabsMenu(labels, titles, parent_div, tab_content_id = null) {
  // Menu
  var ul = document.createElement('ul');
  ul.className = 'nav nav-pills nav-justified';
  ul.setAttribute('data-tabs', 'tabs');
  for (var i = 0; i < labels.length; i++) {
    var li = document.createElement('li');
    if (i == 0) {
      li.className = 'active';
    }
    var text = document.createTextNode(titles[i]);
    var elem = document.createElement('a');
    elem.appendChild(text);
    elem.setAttribute('href', '#' + labels[i]);
    elem.setAttribute('data-toggle', 'pill');
    li.appendChild(elem);
    ul.appendChild(li);
  }
  parent_div.appendChild(ul);
  // Div for each tab
  var tabs_content = createDivWithClass(tab_content_id, 'tab-content', parent_div);
  for (var i = 0; i < labels.length; i++) {
      var tab_class = 'tab-pane fade';
      if (i == 0) {
        tab_class += ' in active';
      }
      var tab = createDivWithClass(labels[i], tab_class, tabs_content);
  }
}

// Remove all the elements from a div
function cleanDiv(div_name) {
  var div_content = $('#' + div_name)[0];
  if (!div_content) {
      return;
  }
  while (div_content !== null && div_content.hasChildNodes()) {
    div_content.removeChild(div_content.firstChild);
  }
  return div_content;
}

function createSelectList(id, size, callback, parent_div, label = null,
        multiple = false) {
    var form_group = createDivWithClass('', 'form-group');
    parent_div.appendChild(form_group);
    if (label) {
        var l = document.createElement('label');
        l.setAttribute('for', id);
        l.innerHTML = label;
        form_group.appendChild(l);
    }
    var select = document.createElement('SELECT');
    select.setAttribute('class', 'form-control');
    if (multiple) {
      select.setAttribute('multiple', 'multiple');
    }
    select.setAttribute('id', id);
    select.setAttribute('size', size);
    select.addEventListener('change', callback);
    form_group.appendChild(select);
    return select;
}

function addElementsToSelectList(selector_id, list) {
  var selector = cleanDiv(selector_id);
  list.forEach(function(e) {
    addElementToSelectList(selector, e);
  });
}

function addElementToSelectList(selector, e, selected = false) {
    var opt = document.createElement('option');
    opt.text = e;
    opt.value = e;
    opt.selected = selected;
    selector.add(opt);
}

function getSelectedOption(selector) {
    if (selector == null) {
        console.log('Unknown selector');
        return null;
    } else if (selector.selectedIndex == -1) {
        console.log('No element selected');
        return null;
    } else {
        return $('#' + selector.id).val();
    }
}
