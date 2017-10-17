function drawDensity(div_name, get_path, log, get_xlabel) {
  cleanDiv(div_name);
  d3.json(get_path(), function(error, data) {
    if (!('x_density' in data) && !('x_log_density' in data)) {
      printStatistics(data, div_name);
    } else {
      printDensity(div_name, log, get_xlabel, data);
    }
  });
}

function printDensity(div_name, log, get_xlabel, data) {

  var margin = {top: 20, right: 20, bottom: 30, left: 40};
  var width = 300 - margin.left - margin.right;
  var height = 300 - margin.top - margin.bottom;

  // add the graph canvas to the body of the webpage
  var svg = d3.select('#' + div_name).append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  if (log) {
    var xValue = data.x_log_density;
    var yValue = data.y_log_density;
  } else {
    var xValue = data.x_density;
    var yValue = data.y_density;
  }

  var xScale = d3.scale.linear().range([0, width]);
  xScale.domain(d3.extent(xValue));
  var xMap = xValue.map(xScale);
  var xAxis = d3.svg.axis()
    .scale(xScale)
    .ticks(5)
    .orient('bottom');

  var yScale = d3.scale.linear().range([height, 0]);
  yScale.domain(d3.extent(yValue));
  var yMap = yValue.map(yScale);
  var yAxis = d3.svg.axis()
    .scale(yScale)
    .ticks(5)
    .orient('left');

  // x-axis
  svg.append('g')
    .attr('class', 'x axis')
    .attr('transform', 'translate(0,' + height + ')')
    .call(xAxis)
    .append('text')
    .attr('class', 'label')
    .attr('x', width)
    .attr('y', -6)
    .style('text-anchor', 'end')
    .text(get_xlabel());

  // y-axis
  svg.append('g')
    .attr('class', 'y axis')
    .call(yAxis)
    .append('text')
    .attr('class', 'label')
    .attr('transform', 'rotate(-90)')
    .attr('y', 6)
    .attr('dy', '.71em')
    .style('text-anchor', 'end')
    .text('density');

  for (i in xMap) {
    x = xMap[i];
    y = yMap[i];
    svg.append('circle')
      .attr('cx', x)
      .attr('cy', y)
      .attr('r', 2);
  }
}

function printStatistics(data, div_name) {
  $('#' + div_name)[0].innerHTML = JSON.stringify(data, undefined, 2);
}

function addCallbackOnDensityRadioButtonSelectList(name, select_list_names) {
  addCallbackOnDensityRadioButton(name);
  addCallbackOnDensitySelectLists(name, select_list_names);
}

function addCallbackOnDensityRadioButton(name) {
  var div_name = name + '_density';
  var button_log = $('#' + name + '_radio_log')[0];
  var button_linear = $('#' + name + '_radio_linear')[0];
  var get_path = get_density(button_log, div_name);
  var get_xlabel = function() { return name; };
  // Add callback to log radio button
  button_log.addEventListener('click', function() {
    drawDensity(div_name, get_path, true, get_xlabel);
  });
  // Add callback to linear radio button
  button_linear.addEventListener('click', function() {
    drawDensity(div_name, get_path, false, get_xlabel);
  });
  // Draw the log density
  drawDensity(div_name, get_path, button_log.checked, get_xlabel);
}

function addCallbackOnDensitySelectLists(name, select_list_names) {
  var div_name = name + '_density';
  var button_log = $('#' + name + '_radio_log')[0];
  var get_path = get_density(button_log, div_name);
  var get_xlabel = function() { return name; };
  for (i in select_list_names) {
    var select_list_name = select_list_names[i];
    var select_list = $('#' + select_list_name)[0];
    select_list.addEventListener('change', function() {
      var log = button_log.checked;
      drawDensity(div_name, get_path, log, get_xlabel);
    });
  }
}
