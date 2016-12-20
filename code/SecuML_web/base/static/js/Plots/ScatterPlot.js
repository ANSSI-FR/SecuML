function drawScatterPlot(div_name, get_path, xlabel, ylabel,
        click_instance_callback) {

  var plot = cleanDiv(div_name);

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
    yScale.domain(d3.extent(data, function(d) {return d.y} ));

    var color = function(d) { return d.color; };

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
    .on('click', function(d) {
        click_instance_callback(Math.floor(d.id), Math.floor(d.cluster))();
    });
  });
}
