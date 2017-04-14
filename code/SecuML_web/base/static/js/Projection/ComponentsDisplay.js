function drawComponentsInterpretation(project, dataset, experiment,
        c_x, c_y) {

  var C_x = 'C_' + c_x;
  var C_y = 'C_' + c_y;

  cleanDiv('components_interpretation_graph');

  var components_coefficient_file = buildQuery('getProjectionMatrix',
          [project, dataset, experiment]);
  d3.csv(components_coefficient_file, function(error, data) {

    var margin = {top: 20, right: 20, bottom: 30, left: 40};
    var width = 300 - margin.left - margin.right;
    var height = 300 - margin.top - margin.bottom;

    var xValue = function(d) { return d[C_x];};
    var xScale = d3.scale.linear().domain([-1,1]).range([0, width]);
    var xMap = function(d) { return xScale(xValue(d));};
    var xAxis = d3.svg.axis().scale(xScale).orient('bottom');

    var yValue = function(d) { return d[C_y];};
    var yScale = d3.scale.linear().domain([-1,1]).range([height, 0]);
    var yMap = function(d) { return yScale(yValue(d));};
    var yAxis = d3.svg.axis().scale(yScale).orient('left');

    // add the graph canvas to the body of the webpage
    var svg = d3.select(
      '#components_interpretation_graph').append('svg')
      .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    // change string (from CSV) into number format
    data.forEach(function(d) {
      d[C_x] = +d[C_x];
      d[C_y] = +d[C_y];
    });

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
      .text(C_x);

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
      .text(C_y);

    // draw dots
    svg.selectAll('.dot')
      .data(data)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('r', 2)
      .attr('cx', xMap)
      .attr('cy', yMap)
      .style('fill', 'black')
      .on('mouseover', function(d) {
        tooltip.transition()
        .duration(200)
        .style('opacity', .9);
      tooltip.html(d.feature + '<br/>')
        .style('left', (d3.event.pageX + 5) + 'px')
        .style('top', (d3.event.pageY - 28) + 'px')
        .style('color', 'red');
      })
    .on('mouseout', function(d) {
      tooltip.transition()
      .duration(500)
      .style('opacity', 0);
    });
  });
}

function drawProjectionOnComponents(project, dataset, experiment,
        c_x, c_y) {

  if (c_y <= c_x) {
    alert('C_x must be smaller than C_y');
    return;
  }

  var C_x = 'C_' + c_x;
  var C_y = 'C_' + c_y;

  cleanDiv('projected_data_graph');

  hex_bin_file = buildQuery('getHexBin',
          [project, dataset, experiment, c_x, c_y]);

  var margin = {top: 20, right: 20, bottom: 30, left: 40};
  var width = 500 - margin.left - margin.right;
  var height = 300 - margin.top - margin.bottom;

  // add the graph canvas to the body of the webpage
  var svg = d3.select('#projected_data_graph').append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  // Print the PC projections
  d3.json(hex_bin_file, function(error, data) {
    if (error) return console.warn(error);
    var xmin = data[0].xmin;
    var xmax = data[0].xmax;
    var ymin = data[0].ymin;
    var ymax = data[0].ymax;

    //// setup x
    var x = d3.scale.linear().domain([xmin, xmax]).range([0, width]);
    var xAxis = d3.svg.axis().scale(x).orient('bottom');

    //// setup y
    var y = d3.scale.linear().domain([ymin, ymax]).range([height, 0]);
    var yAxis = d3.svg.axis().scale(y).orient('left');

    var color_hex = d3.scale.linear()
    .domain([0, 100])
    .range(['GreenYellow', 'black']);

    var color_malicious = d3.scale.linear()
    .domain([0, 1])
    .range(['yellow', 'red']);

  function scalePoints(points) {
    new_points = [];
    for (var i in points) {
      var point = points[i];
      new_point = [0, 0];
      new_point[0] = x(point[0]);
      new_point[1] = y(point[1]);
      new_points[new_points.length] = new_point;
    }
    return new_points;
  }

  // change string (from Json) into number format
  data.forEach(function(d) {
    d.num_instances = +d.num_instances;
    for (var p in d.hexagons) {
      d.hexagons[0] = +p[0];
      d.hexagons[1] = +p[1];
    }
  });

  var hexagons = svg.selectAll('polygon')
    .data(data)
    .enter()
    .append('polygon')
    .attr('points', function (d) { return scalePoints(d.hexagon); })
    .style('fill', function (d) {
        return color_hex(d.num_malicious_instances + d.num_ok_instances); })
    .on('mouseover', function(d) {
      tooltip.transition()
        .duration(200)
        .style('opacity', .9);
      tooltip.html(d.num_ok_instances + ',' + d.num_malicious_instances)
        .style('left', (d3.event.pageX + 5) + 'px')
        .style('top', (d3.event.pageY - 28) + 'px');
      d3.select(this).style('cursor', 'pointer');
    })
  .on('mouseout', function(d) {
    tooltip.transition()
      .duration(500)
      .style('opacity', 0);
    d3.select(this).style('cursor', 'default');
  })
  .on('click', function(d) {
    cleanInstanceInformation();
    if (d.num_malicious_instances + d.num_ok_instances > 1000) {
      return;
    } else {
      displayInstancesList('malicious', d.malicious_instances);
      displayInstancesList('ok', d.ok_instances);
    }
  });

  var circle = svg.selectAll('circle')
      .data(data)
      .enter()
      .append('circle')
      .attr('cx', function (d) { if (d.hasOwnProperty('center')) return x(d.center[0]); })
      .attr('cy', function (d) { if (d.hasOwnProperty('center')) return y(d.center[1]); })
      .style('fill', function (d) {
          if (d.hasOwnProperty('prop_malicious')) {
            return color_malicious(d.prop_malicious);
          }})
      .attr('r', 2);

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
    .text(C_x);

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
    .text(C_y);

  });

}

function drawComponents(project, dataset, experiment, c_x, c_y) {
  drawProjectionOnComponents(project, dataset, experiment, c_x, c_y);
  //drawComponentsInterpretation(project, dataset, experiment, c_x, c_y);
}
