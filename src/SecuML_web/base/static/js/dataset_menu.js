var path = window.location.pathname.split('/');
var project = path[2];
var dataset = path[3];

var menu = $('#menu')[0];

var title = $('#title')[0];
title.appendChild(document.createTextNode('SecuML - ' + project + ' - ' + dataset));
var panel = createPanel('panel-primary', null, 'Select an experiment', menu);

var query = buildQuery('getAllExperiments', [project, dataset]);
$.getJSON(query,
          function(data) {
            var kinds = Object.keys(data);
            for (var i in kinds) {
                var kind = kinds[i];
                if (kind == 'Validation') {
                    continue;
                }
                var panel_kind = createCollapsingPanel('panel-info', null, kind,
                                             panel, kind + '-collapse');
                var ul_kind = createDivWithClass(null, 'list-group',
                                                 parent_div = panel_kind);
                var experiments = data[kind];
                for (var i = 0; i < experiments.length; i++) {
                  var exp = experiments[i];
                  var id = exp.id;
                  var name = exp.name;
                  var li = document.createElement('a');
                  li.setAttribute('class', 'list-group-item');
                  var exp_name = name;
                  if (exp_name.length > 150) {
                      exp_name = exp_name.substring(0, 150) + '...';
                  }
                  exp_name = id + ', ' + exp_name;
                  var e_text = document.createTextNode(exp_name);
                  li.appendChild(e_text);
                  var exp_query = buildQuery('SecuML', [id]);
                  li.setAttribute('href', exp_query);
                  ul_kind.appendChild(li);
                }

            }
          }
);
