function barPlotOptions(data, xlabel, ylabel) {
    var options = {
        responsive: true,
        maintainAspectRatio: false,
        tooltips: {
            mode: 'label',
            backgroundColor: 'rgba(0,0,0,0.5)',
            bodySpacing: 5,
        },
        legend: {
            display: true,
        },
        hover: {
            mode : '',
        },
        scales: {
            xAxes: [{
                display: true,
                labelString: xlabel,
                barPercentage: .85,
                categoryPercentage: .65,
                gridLines: {
                    display: false
                },
                stacked: false
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
    return options
}

function barPlotAddTooltips(options, tooltips_data=false) {
    var tooltips_function = function(tooltipItem, data) {
        if (tooltips_data) {
            return String(tooltips_data[tooltipItem.index]);
        } else {
            return data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
        }
    }
    options.tooltips.callbacks = {label: tooltips_function};
}

function barPlotAddBands(options, bands) {
    if (bands) {
        options.bands = {yValue: 0,
                         bandLine: {stroke: 2,
                                    colour: 'black'},
                                    belowThresholdColour: ['#5cb85c']
                        };
    }
}

function drawBarPlot(div_name, options, data, type='bar', width=null,
        height=null, callback=null) {
    cleanDiv(div_name);
    var canvas = document.createElement('canvas');
    canvas.setAttribute('id', div_name + '_hist');
    if (width) {
        canvas.setAttribute('width', width);
    }
    if (height) {
        canvas.setAttribute('height',  height);
    }
    $('#' + div_name)[0].appendChild(canvas);
    // Get the context of the canvas element we want to select
    var ctx = $('#' + div_name + '_hist')[0].getContext('2d');
    var myBarChart = new Chart(ctx, {type: type,
                                     data: data,
                                     options: options});
    if (callback) {
        addCallbackToBarplot(canvas, myBarChart, callback);
    }
    return [canvas, myBarChart];
}

function addCallbackToBarplot(canvas, myBarChart, callback) {
    canvas.onclick = function(evt){
        var active_bars = myBarChart.getElementsAtEvent(evt)
            if (active_bars.length > 0) {
                callback(active_bars);
            }
    };
}
