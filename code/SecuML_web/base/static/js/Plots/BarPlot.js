function drawBarPlotFromPath(div_name, get_path, xlabel, ylabel, no_label, callback,
        width = '290', height = '300') {
    cleanDiv(div_name);
    if (no_label) {
        var options = {
            responsive: false,
            scales: {
                xAxes: [{
                    display: true,
                    labelString: xlabel,
                    barPercentage: .5,
                    categoryPercentage: 0.8,
                    gridLines: {
                        display: false
                    }
                }],
                yAxes: [{
                    display: true,
                    labelString: ylabel,
                    gridLines: {
                        display: false
                    }
                }]
            }
        };
    } else {
        var options = {
            //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
            responsive: false,
            tooltips: {
                mode: 'label',
                backgroundColor: 'rgba(0,0,0,0.5)',
                bodySpacing: 5,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return tooltipItem.yLabel
                    }
                }
            },
            scales: {
                xAxes: [{
                    display: true,
                    labelString: xlabel,
                    barPercentage: .75,
                    categoryPercentage: .55,
                    gridLines: {
                        display: false
                    }
                }],
                yAxes: [{
                    display: true,
                    labelString: ylabel,
                    gridLines: {
                        display: false
                    }
                }]
            }
        };
    }

    d3.json(get_path, function(error, data) {
        var canvas = document.createElement('canvas');
        canvas.setAttribute('id', div_name + '_hist');
        canvas.setAttribute('width', width);
        canvas.setAttribute('height', height);
        $('#' + div_name)[0].appendChild(canvas);
        // Get the context of the canvas element we want to select
        var ctx = $('#' + div_name + '_hist')[0].getContext('2d');
        var myBarChart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: options
        });

        canvas.onclick = function(evt){
            var activeBars = myBarChart.getElementsAtEvent(evt)
            if (activeBars.length >0){
                //console.log('index', activeBars[0]._index);
                //console.log('dataset', activeBars[0]._datasetIndex);
            }
        };

    });
}

function drawBarPlot(div_name, data, tooltips_data = false) {
    cleanDiv(div_name);
    var tooltips_function = function(tooltipItem, data) {
        if (tooltips_data) {
            //$('#' + div_name)[0].appendChild(document.createTextNode(String(tooltips_data[tooltipItem.xLabel])));
            return String(tooltips_data[tooltipItem.xLabel]);
        } else {
            return tooltipItem.yLabel;
        }
    }

    var options = {
        responsive: false,
        maintainAspectRatio:false,
        tooltips: {
            mode: 'label',
            backgroundColor: 'rgba(0,0,0,0.5)',
            bodySpacing: 5,
            callbacks: {
                label: tooltips_function
                }
        },
        legend: {
            display: false,
        },
        hover: {
            mode : '',
        },
        scales: {
            xAxes: [{
                display: false,
                barPercentage: .85,
                categoryPercentage: .65,
                gridLines: {
                    display: false
                },
                stacked: true
            }],
            yAxes: [{
                display: true,
                gridLines: {
                    display: false
                }
            }]
        },
        bands: {
            yValue: 0,
            bandLine: {
                stroke: 0.1,
                colour: 'black'
            },
            belowThresholdColour: [
                'green',
            ]
        }
    };

    var canvas = document.createElement('canvas');
    canvas.setAttribute('id', div_name + '_hist');
    //canvas.setAttribute('width', '500');
    //canvas.setAttribute('height', '530');
    $('#' + div_name)[0].appendChild(canvas);
    // Get the context of the canvas element we want to select
    var ctx = $('#' + div_name + '_hist')[0].getContext('2d');
    var myBarChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
    return [canvas, myBarChart];
}
