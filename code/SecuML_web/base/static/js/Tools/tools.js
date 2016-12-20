function isProbability(p) {
    return !isNaN(p) && p > 0 && p < 1;
}

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}

function isInList(elem, list) {
  for (i in list) {
      l = list[i];
      if (l == elem) {
          return true;
      }
  }
  return false;
}

function get_density(log_radio_button, filename) {
  return function() {
    var label = get_label();
    var lin_log = get_lin_log(log_radio_button);
    var path = '/stats/getDensity/' + database_name + '/' + label
    path += '/' + filename + '/' + lin_log + '/'; 
    return path;
  }
}

function get_pie(filename) {
  return function() {
  var label = get_label();
  var path = '/stats/getPie/' + database_name + '/';
  path += label + '/' + filename + '/';
  return path;
  }
}
