var project = window.location.pathname.split('/')[2];
var dataset = window.location.pathname.split('/')[3];
var exp_type = window.location.pathname.split('/')[4];

var menu = $('#menu')[0];

var title = $('#title')[0];
title.appendChild(document.createTextNode(project + ' ' + dataset));

var ul = document.createElement('ul');
var query = buildQuery('getExperimentsNames', 
                [project, dataset, exp_type]);
d3.json(query, function(error, data) {
    var experiments = Object.keys(data);
    for (i in experiments) {
        var experiment = experiments[i];
        var id = data[experiment]
        var li = document.createElement('li');
        var e_elem = document.createElement('a');
        var e_text = document.createTextNode(experiment);
        e_elem.appendChild(e_text);
        var exp_query = buildQuery('SecuML', 
                        [project, dataset, id]);
        e_elem.setAttribute('href', exp_query);
        li.appendChild(e_elem);
        ul.appendChild(li);
    }
});
menu.appendChild(ul);
