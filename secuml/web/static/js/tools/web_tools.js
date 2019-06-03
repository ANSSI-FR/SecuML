function addPrevNextShortcuts(){
  $(document).keypress(function (e) {
     var key = e.keyCode;
     if(key == 13){
        $('#ok_button').click();
        return false;
     } else if(key == 39){
        $('#next_button').click();
        return false;
     } else if(key == 37){
        $('#prev_button').click();
        return false;
     }
  });
}

function generateTitle(title) {
  var row_title = $('#row_title')[0];
  var div = createDivWithClass(null, 'page-header', parent_div=row_title);
  var h1 = document.createElement('h1');
  h1.textContent = title;
  div.appendChild(h1);
}

function upperCaseFirst(str) {
  return str.charAt(0).toUpperCase() + str.substring(1);
}

function buildQuery(name, args) {
  query  = '/' + name + '/';
  if (args) {
    query += args.join('/') + '/';
  }
  return query;
}

function addTitle(div, title) {
  var h = document.createElement('h4');
  h.textContent = title;
  div.appendChild(h);
}

function createDiv(id, parent_div=null, title=null) {
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

function createDivWithClass(id, classname, parent_div=null, title=null) {
    var div = createDiv(id, parent_div=parent_div, title=title);
    div.setAttribute('class', classname);
    return div;
}

function createPanel(panel_type, col_size, heading, parent_div, body_id,
                     return_heading=false, href=null) {
  if (col_size) {
    var col = createDivWithClass(null, col_size, parent_div);
    parent_div = col;
  }
  var panel = createDivWithClass(null, 'panel ' + panel_type,
                                 parent_div=parent_div);
  if (heading) {
    var panel_heading = createDivWithClass(null, 'panel-heading',
                                           parent_div=panel);
    var panel_ref = panel_heading;
    if (href) {
      panel_ref = document.createElement('a');
      panel_ref.setAttribute('class', 'panel-title');
      panel_ref.href = href;
      panel_heading.appendChild(panel_ref);
    }
    if (typeof heading == 'string') {
      var panel_title = document.createElement('h3');
      panel_title.setAttribute('class', 'panel-title');
      panel_title.textContent = heading;
      panel_ref.appendChild(panel_title);
    } else {
      panel_heading.appendChild(heading);
    }
  }
  var panel_body = createDivWithClass(null, 'panel-body', parent_div=panel);
  panel_body.setAttribute('id', body_id);
  if (return_heading) {
    return [panel_body, panel_title];
  } else {
    return panel_body;
  }
}

function createCollapsingPanel(panel_type, col_size, heading, parent_div,
                               collapse_id) {
  if (col_size) {
    var col = createDivWithClass(null, col_size, parent_div);
    parent_div = col;
  }
  var panel_group = createDivWithClass(null, 'panel_group', parent_div);

  var panel = createDivWithClass(null, 'panel ' + panel_type,
                                 parent_div=panel_group);

  var title_link = document.createElement('a');
  title_link.setAttribute('data-toggle', 'collapse');
  title_link.appendChild(document.createTextNode(heading));
  title_link.href = '#' + collapse_id + '_collapse';

  var panel_heading = createDivWithClass(null, 'panel-heading',
          parent_div=panel);
  var panel_title = document.createElement('h3');
  panel_title.setAttribute('class', 'panel-title');
  panel_title.appendChild(title_link);
  panel_heading.appendChild(panel_title);

  var panel_collapse = createDivWithClass(collapse_id + '_collapse',
                                          'panel-collapse collapse',
                                          panel);
  var panel_body = createDivWithClass(collapse_id,
                                      'panel-body',
                                      panel_collapse);
  return panel_body;
}

function createTable(div_name, titles, table_id=null, width=null) {
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

function addRow(body, elements, ids=null, title=false, row_class=null) {
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
    if (ids) {
        td.id = ids[i];
    }
    tr.appendChild(td);
  }
  body.appendChild(tr);
}

function createTabsMenu(labels, titles, parent_div, tab_content_id=null) {
  // Menu
  var ul = document.createElement('ul');
  ul.className = 'nav nav-pills nav-justified';
  ul.setAttribute('data-tabs', 'tabs');
  for (var i = 0; i < labels.length; i++) {
    var li = document.createElement('li');
    li.id = 'tab_' + labels[i];
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
  var tabs_content = createDivWithClass(tab_content_id, 'tab-content',
                                        parent_div);
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

function createRadioList(name, labels, ids, callback, parent_div,
                         selected_id=null) {
    var form_group = createDivWithClass(null, 'form-group');
    parent_div.appendChild(form_group);
    for (var i = 0; i < labels.length; i++) {
        var l = document.createElement('label');
        l.setAttribute('class', 'radio-inline');
        l.innerHTML = '<input type="radio" name="' + name + '" id="' + ids[i] + '" value="' + labels[i] + '">' + labels[i];
        l.addEventListener('change', callback);
        form_group.appendChild(l);
    };
    if (! selected_id) {
        document.getElementById(ids[0]).checked = true;
    } else {
        document.getElementById(selected_id).checked = true;
    }
}

function getSelectedRadioButton(ids) {
    for (var i = 0; i < ids.length; i++) {
        var e = document.getElementById(ids[i]);
        if (e.checked) {
            return e.value;
        }
    }
}

function createSelectList(id, size, callback, parent_div, label=null,
        multiple=false, with_search=false) {
    var form_group = createDivWithClass('', 'form-group');
    parent_div.appendChild(form_group);
    if (label) {
        var l = document.createElement('label');
        l.setAttribute('for', id);
        l.innerHTML = label;
        form_group.appendChild(l);
    }
    if (with_search) {
        var search_input = document.createElement('input');
        search_input.setAttribute('class', 'form-control');
        search_input.setAttribute('id', id + '_search');
        search_input.setAttribute('type', 'text');
        search_input.setAttribute('placeholder', 'Search ...');
        form_group.appendChild(search_input);
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
    if (with_search) {
        $(document).ready(function(){
            $('#' + id + '_search').on('keyup', function() {
            var value = $(this).val().toLowerCase();
            $('#' + id + ' option').filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
            });});
        });
    }
    return select;
}

// list: the ids of the elements
// text: the text of the elements
function addElementsToSelectList(selector_id, list, text=null) {
  var selector = cleanDiv(selector_id);
  if (list.length == 0) {
    return;
  }
  for (var i = 0; i < list.length; i++) {
    var t = null;
    if (text != null) {
        t = text[i];
    }
    addElementToSelectList(selector, list[i], false, t);
  }
}

function addElementToSelectList(selector, e, selected=false, text=null) {
    var opt = document.createElement('option');
    opt.value = e;
    if (text != null) {
        opt.text = text;
    } else {
        opt.text = e;
    }
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

function displayAlert(alert_id, title, body) {

    parent_div = document.body;

    var modal_div = createDivWithClass(alert_id, 'modal fade', parent_div);
    modal_div.setAttribute('tabindex', '-1');
    modal_div.setAttribute('role', 'dialog');

    var modal_dialog_div = createDivWithClass(
                    null,
                    'modal-dialog modal-dialog-centered',
                    modal_div)
    modal_dialog_div.setAttribute('role', 'document');
    var modal_content_div = createDivWithClass(null,
                                               'modal-content',
                                               modal_dialog_div)
    // Header
    var modal_header_div = createDivWithClass(null,
                                              'modal-header',
                                              modal_content_div)

    var close_button = document.createElement('button');
    modal_header_div.appendChild(close_button);
    close_button.setAttribute('class', 'close');
    close_button.setAttribute('data-dismiss', 'modal');
    close_button.innerHTML = '&times;';

    var modal_h5 = document.createElement('h4');
    modal_h5.setAttribute('class', 'modal-title');
    var title_text = document.createTextNode(title);
    modal_h5.appendChild(title_text);
    modal_header_div.appendChild(modal_h5);

    // Body
    var modal_body_div = createDivWithClass(null,
                                            'modal-body',
                                            modal_content_div);
    for (var b in body) {
      var para = document.createElement('p');
      var body_text = document.createTextNode(body[b]);
      para.appendChild(body_text);
      modal_body_div.appendChild(para);
    }

    //// Footer
    //var modal_footer_div = createDivWithClass(null, 'modal-footer', modal_content_div);
    //var close_button = document.createElement('button');
    //modal_footer_div.appendChild(close_button);
    //close_button.setAttribute('class', 'btn btn-default');
    //close_button.setAttribute('type', 'button');
    //close_button.setAttribute('data-dismiss', 'modal');
    //close_button.innerHTML = 'Close';

    $('#' + alert_id).modal({
        show: true,
        backdrop: true
    });
}
