function drawComponentsSelectors(num_components, callback) {

  console.log(num_components);

  var select_comp_div = cleanDiv('select_components');

  // Add the selector lists for c_x and c_y
  // By default, c_x = 0 and c_y = 1
  var c_x = document.createElement('SELECT');
  var c_y = document.createElement('SELECT');
  c_x.setAttribute('id', 'cx_select');
  c_y.setAttribute('id', 'cy_select');

  for (var i = 0; i < num_components; i++) {
    var opt_x = document.createElement('option');
    opt_x.text = 'C_' + i;
    opt_x.value = i;
    c_x.add(opt_x);
    var opt_y = document.createElement('option');
    opt_y.text = 'C_' + i;
    opt_y.value = i;
    c_y.add(opt_y);
  }
  c_x.value = 0;
  c_y.value = 1;

  c_x_selected = c_x.options[c_x.selectedIndex].text;
  c_y_selected = c_y.options[c_y.selectedIndex].text;

  // Button to validate the choice of the principle components
  var ok_button = document.createElement('BUTTON');
  var ok_text = document.createTextNode('OK');
  ok_button.appendChild(ok_text);
  ok_button.addEventListener('click', callback(c_x, c_y));

  div_select = document.createElement('div');
  div_select.appendChild(c_x);
  div_select.appendChild(c_y);
  div_select.appendChild(ok_button);
  select_comp_div.appendChild(div_select);

  var prev_button = document.createElement('BUTTON');
  var prev_text = document.createTextNode('PREV');
  prev_button.appendChild(prev_text);
  prev_button.addEventListener('click', function() {
      if (c_x.selectedIndex - 1 >= 0 && c_y.selectedIndex -1 >= 0) {
              c_x.selectedIndex -= 1;
              c_y.selectedIndex -= 1;
              callback(c_x, c_y)();
      }
  });
  var next_button = document.createElement('BUTTON');
  var next_text = document.createTextNode('NEXT');
  next_button.appendChild(next_text);
  next_button.addEventListener('click', function() {
      if (c_x.selectedIndex + 1 < num_components &&
          c_y.selectedIndex + 1 < num_components) {
              c_x.selectedIndex += 1;
              c_y.selectedIndex += 1;
              callback(c_x, c_y)();
      }
  });
  div_prev_next = document.createElement('div');
  div_prev_next.appendChild(prev_button);
  div_prev_next.appendChild(next_button);
  select_comp_div.appendChild(div_prev_next);;

  var rand_button = document.createElement('BUTTON');
  var rand_text = document.createTextNode('RAND');
  rand_button.appendChild(rand_text);
  rand_button.addEventListener('click', function() {
      var found = false;
      if (num_components == 2) {
          found = true;
      }
      while (!found) {
          c_x.selectedIndex = getRandomInt(0, num_components-1);
          c_y.selectedIndex = getRandomInt(0, num_components-1);
          found = c_x.selectedIndex < c_y.selectedIndex;
      }
      callback(c_x, c_y)();
  });
  div_rand = document.createElement('div');
  div_rand.appendChild(rand_button);
  select_comp_div.appendChild(div_rand);
}
