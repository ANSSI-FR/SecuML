var path = window.location.pathname.split('/');
var project  = path[2];

var menu = $('#menu')[0];

var title = $('#title')[0];
title.appendChild(document.createTextNode('SecuML - ' + project));
var panel = createPanel('panel-primary', 'col-md-6', 'Select a dataset', menu);

var div = document.createElement('div');
div.setAttribute('class', 'list-group');
panel.appendChild(div);

var query = buildQuery('getDatasets', [project]);
$.getJSON(query,
          function(data) {
            var datasets = data['datasets'];
            for (var i = 0; i < datasets.length; i++) {
                var dataset = datasets[i];
                var li = document.createElement('a');
                li.setAttribute('class', 'list-group-item');
                var dataset_query = buildQuery('SecuML', [project, dataset,
                                                          'menu']);
                li.setAttribute('href', dataset_query);
                var e_text = document.createTextNode(dataset);
                li.appendChild(e_text);
                div.appendChild(li);


            }
          }
);
