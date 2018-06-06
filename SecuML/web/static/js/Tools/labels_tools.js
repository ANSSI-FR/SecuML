function otherLabel(label) {
    if (label == 'malicious') {
        return 'benign';
    } else {
        return 'malicious';
    }
}

function hasGroundTruth(experiment_id) {
  var query = buildQuery('hasGroundTruth', [experiment_id]);
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open('GET', query, false);
  xmlHttp.send(null);
  var has_ground_truth = xmlHttp.responseText;
  return has_ground_truth == 'True';
}
