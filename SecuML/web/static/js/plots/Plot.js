function drawPlot(div_name, get_path, xlabel, ylabel, yscale_0_1) {

  var color = 'black';

  var plot = $('#' + div_name)[0];
  while (plot.firstChild) {
    plot.removeChild(plot.firstChild);
  }

  var margin = {top: 20, right: 20, bottom: 30, left: 40};
  var width = 300 - margin.left - margin.right;
  var height = 300 - margin.top - margin.bottom;

  var svg = d3.select('#' + div_name).append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  d3.csv(get_path(), function(error, data) {

    // change string (from CSV) into number format
    data.forEach(function(d) {
      d.x = +d.x;
      d.y = +d.y;
    });

    var xValue = function(d) { return d.x;};
    var xScale = d3.scale.linear().range([0, width]);
    var xMap = function(d) { return xScale(xValue(d));};
    var xAxis = d3.svg.axis().scale(xScale).orient('bottom');
    xScale.domain(d3.extent(data, function(d) {return d.x} ));

    var yValue = function(d) { return d.y;};
    var yScale = d3.scale.linear().range([height, 0]);
    var yMap = function(d) { return yScale(yValue(d));};
    var yAxis = d3.svg.axis().scale(yScale).orient('left');
    if (yscale_0_1()) {
      yScale.domain([0,1]);
    } else {
      yScale.domain(d3.extent(data, function(d) {return d.y} ));
    }

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
      .text(xlabel);

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
    .text(ylabel);

  // draw dots
  svg.selectAll('.dot')
    .data(data)
    .enter().append('circle')
    .attr('class', 'dot')
    .attr('r', 2)
    .attr('cx', xMap)
    .attr('cy', yMap)
    .style('fill', color)
    .style('stroke', color)
    .on('mouseover', function(d) {
      tooltip.transition()
      .duration(200)
      .style('opacity', .9);
    tooltip.html(d.y + '<br/>')
      .style('left', (d3.event.pageX + 5) + 'px')
      .style('top', (d3.event.pageY - 28) + 'px')
      .style('color', 'red');
    })
  .on('mouseout', function(d) {
    tooltip.transition()
    .duration(500)
    .style('opacity', 0);
  });

  // draw lines between dots
  var valueline = d3.svg.line()
    .x(xMap)
    .y(yMap)
    .interpolate('linear');
  svg.append('path')
    .attr('d', valueline(data))
    .attr('stroke', color)
    .attr('stroke-width', 2)
    .attr('fill', 'none');

  });
}

function addCallBackOnPlotSelectList(div_name, get_path,
    select_list_name, xlabel, ylabel, get_yscale_0_1) {
  var select_list = $('#' + select_list_name)[0];
  select_list.addEventListener('change', function() {
    drawPlot(div_name, get_path, xlabel, ylabel, get_yscale_0_1);
  });
  drawPlot(div_name, get_path, xlabel, ylabel, get_yscale_0_1);
}
