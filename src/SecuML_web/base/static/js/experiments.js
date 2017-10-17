var path = window.location.pathname.split('/');
var project  = path[2];
var dataset  = path[3];
var exp_type = path[4];

var menu = $('#menu')[0];

var title = $('#title')[0];
title.appendChild(document.createTextNode(project + ' ' + dataset));

var ul = document.createElement('ul');
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
                  var li = document.createElement('li');
                  var e_elem = document.createElement('a');
                  var e_text = document.createTextNode(experiment);
                  e_elem.appendChild(e_text);
                  var exp_query = buildQuery('SecuML', [id]);
                  e_elem.setAttribute('href', exp_query);
                  li.appendChild(e_elem);
                  ul.appendChild(li);
                }
            }
          });
menu.appendChild(ul);
