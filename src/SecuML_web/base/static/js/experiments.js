var path = window.location.pathname.split('/');
var project  = path[2];
var dataset  = path[3];
var exp_type = path[4];

var menu = $('#menu')[0];

var title = $('#title')[0];
title.appendChild(document.createTextNode(
    project + ' - ' + dataset + ' - ' + exp_type));
var panel = createPanel('panel-primary', null,
                        'Select an experiment', menu);


var div = document.createElement('div');
div.setAttribute('class', 'list-group');
panel.appendChild(div);

var query = buildQuery('getExperimentsNames',
                [project, dataset, exp_type]);
$.getJSON(query,
          function(data) {
            var experiments = Object.keys(data);
            for (var i in experiments) {
                var experiment = experiments[i];
                var ids = data[experiment];
                for (var i = 0; i < ids.length; i++) {
                  var id = ids[i];
                  var li = document.createElement('a');
                  li.setAttribute('class', 'list-group-item');
                  var exp_name = experiment;
                  if (exp_name.length > 150) {
                      exp_name = exp_name.substring(0, 150) + '...';
                  }
                  exp_name = id + ', ' + exp_name;
                  li.appendChild(document.createTextNode(exp_name));
                  var exp_query = buildQuery('SecuML', [id]);
                  li.setAttribute('href', exp_query);
                  div.appendChild(li);
                }
            }
          }
);
