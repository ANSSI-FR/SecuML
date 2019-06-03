var path = window.location.pathname.split('/');
var exp_id = path[2];
var exp_type = 'Test';
var conf = null;

function callback(conf) {
  conf.exp_type = exp_type;
  generateTitle('Detection Results');
  d3.json(buildQuery('getDiademExp', [exp_id]),
          function(data) {
              displayPanels(data.proba, data.with_scoring, data.multiclass,
                            data.perf_monitoring);
              updateMonitoringDisplay('test', exp_id, data.proba,
                                      data.with_scoring, data.multiclass,
                                      data.perf_monitoring, true);
          });
}

function displayPanels(proba, with_scoring, multiclass, perf_monitoring) {
    if (perf_monitoring) {
        var perf_indicators = createPanel(
                             'panel-primary', null, 'Performance Indicators',
                             document.getElementById('perf_indicators'),
                             'test_perf_indicators');
        if (!multiclass) {
            if (proba || with_scoring) {
                var roc = createPanel('panel-primary', null, 'ROC Curve',
                                      document.getElementById('roc'),
                                      'test_roc');
                var far_tpr = createPanel('panel-primary', null,
                                          'FAR-DR Curve',
                                           document.getElementById('far_tpr'),
                                           'test_far_tpr');
            }
            var confusion_matrix = createPanel(
                                  'panel-primary', null, 'Confusion Matrix',
                                  document.getElementById('confusion_matrix'),
                                  'test_confusion_matrix');
        }
    }
    var pred = createPanel('panel-primary', null, 'Predictions',
                           document.getElementById('pred'),
                           'test_pred');
}

loadConfigurationFile(exp_id, callback);
