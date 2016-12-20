function buildQuery(name, args) {
  query  = '/' + name + '/';
  query += args.join('/') + '/';
  return query;
}

function makeRadioButton(name, value, text, checked, callback,
                parent_div = null) {
  var label = document.createElement('label');
  var radio = document.createElement('input');
  radio.setAttribute('id', 'radio_' + value);
  radio.type = 'radio';
  radio.name = name;
  radio.value = value;
  radio.checked = checked;
  radio.addEventListener('change', callback);
  label.appendChild(radio);
  label.appendChild(document.createTextNode(text));
  if (parent_div) {
    parent_div.appendChild(label);
  }
  return label;
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

function createTable(div_name, titles, table_id = null) {
  var items = $('#' + div_name)[0];
  var table = document.createElement('table');
  table.setAttribute('class', 'table');
  if (table_id) {
    table.setAttribute('id', table_id);
  }
  var header = table.createTHead();
  var row = header.insertRow(0);
  for (var i in titles) {
    var cell = row.insertCell(i)
    cell.innerHTML = titles[i]
  }
  items.appendChild(table);
  return table;
}

// Remove all the elements from a div
function cleanDiv(div_name) {
  var div_content = $('#' + div_name)[0];
  while (div_content !== null && div_content.hasChildNodes()) {
    div_content.removeChild(div_content.firstChild);
  }
  return div_content;
}

function createSelectList(id, size, callback, parent_div = null) {
    var select = document.createElement('SELECT');
    select.setAttribute('id', id);
    select.setAttribute('size', size);
    select.addEventListener('change', callback);
    if (parent_div) {
      parent_div.appendChild(select);
    }
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
        return selector[selector.selectedIndex].value;
    }
}
