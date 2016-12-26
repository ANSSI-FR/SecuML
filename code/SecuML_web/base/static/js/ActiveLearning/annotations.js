var project       = window.location.pathname.split('/')[2];
var dataset       = window.location.pathname.split('/')[3];
var experiment_id = window.location.pathname.split('/')[4];
var iteration     = window.location.pathname.split('/')[5];

var hide_confidential = false;

var menu = $('#menu')[0];
var experiment_name = getExperimentName(project, dataset,
                experiment_id);

var ul= document.createElement('ul');
var predicted_labels = ['unsure', 'malicious', 'benign'];
for (l in predicted_labels) {
    try {
       var predicted_label = predicted_labels[l];
       var query = buildQuery('clusteringAnalysis',
           [project, dataset, experiment_id,
           iteration, predicted_label]);
       var xmlHttp = new XMLHttpRequest();
       xmlHttp.open('GET', query, false);
       xmlHttp.send(null);
       var clustering = xmlHttp.responseText == 'True';
       if (clustering) {
         var clustering_experiment =
                 experiment_name + '-' + iteration + '-' + predicted_label;
         var clustering_experiment_id = getExperimentId(
                         project, dataset, clustering_experiment);
         var query = buildQuery('SecuML',
                                 [project, dataset,
                                 clustering_experiment_id]);
         var li = document.createElement('li');
         var s_elem = document.createElement('a');
         var s_text = document.createTextNode(predicted_label);
         s_elem.appendChild(s_text);
         s_elem.setAttribute('href', query);
         li.appendChild(s_elem);
         ul.appendChild(li);
       } else {
         var li = document.createElement('li');
         var s_elem = document.createElement('a');
         if (predicted_label == 'unsure') {
           var label = 'unsure';
         } else {
           var label = data[predicted_label];
         }
         var query = buildQuery('individualAnnotations',
             [project, dataset, experiment_id,
             iteration, predicted_label]);
         var s_text = document.createTextNode(label);
         s_elem.appendChild(s_text);
         s_elem.setAttribute('href', query);
         li.appendChild(s_elem);
         ul.appendChild(li);
       }
    } catch(err) {
        console.log('error with label ' + l);
    }
}
menu.appendChild(ul);
