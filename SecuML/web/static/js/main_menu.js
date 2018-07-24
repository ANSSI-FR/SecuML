var path = window.location.pathname.split('/');

var menu = $('#menu')[0];

var title = $('#title')[0];
title.appendChild(document.createTextNode('SecuML'));
var panel = createPanel('panel-primary', 'col-md-6', 'Select a project', menu);

var div = document.createElement('div');
div.setAttribute('class', 'list-group');
panel.appendChild(div);

var query = buildQuery('getProjects');
$.getJSON(query,
          function(data) {
            var projects = data['projects'];
            if (projects.length == 0) {
                displayAlert('no_project', 'Warning',
                             ['No experiment has been executed yet.',
                              'You should run SecuML experiments from the command line (e.g. SecuML_DIADEM, SecuML_ILAB, or SecuML_clustering)' +
                              ' before displaying the results in the web user interface.']);
            }
            for (var i = 0; i < projects.length; i++) {
                var project = projects[i];
                var li = document.createElement('a');
                li.setAttribute('class', 'list-group-item');
                var project_query = buildQuery('SecuML', [project, 'menu']);
                li.setAttribute('href', project_query);
                var e_text = document.createTextNode(project);
                li.appendChild(e_text);
                div.appendChild(li);
            }
          }
);
