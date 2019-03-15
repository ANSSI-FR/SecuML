.. _misc_detection_perf_metrics:

Detection Performance Metrics
=============================

Classification Error Rate
-------------------------
The most prominent measure of performance is the classification error rate, i.e.
the percentage of misclassified instances,
but it is not suitable in the context of threat detection.
Indeed, the data are usually unbalanced with a small proportion of malicious
instances.

We present an example demonstrating the limits of the classification error rate.
We consider 100 instances: 2 malicious and 98 benign. In this situation, a dumb
detection model predicting always benign has a classification error rate of only
2\% while it is not able to detect any malicious instance.


Confusion Matrix
----------------
To assess properly the performance of a detection method, we must begin by
writing the confusion matrix. The confusion matrix takes into account
the two possible types of errors:
*false negatives*, i.e. malicious instances which have not been detected, and
*false positives*, i.e. benign instances which have triggered a false alarm.

.. figure:: figs/detection_perf_metrics/confusion_matrix.svg
  :width: 70%
  :align: center

  Explanation of the Confusion Matrix.


Detection Rate
--------------
The confusion matrix allows to express performance metrics such as the
*detection rate* and the *false alarm rate*.
There is a consensus on the definition of the *detection rate*,also called
*True Positive Rate (TPR)*:

* :math:`TPR = \frac{TP}{TP + FN}`.

On the contrary, the *false alarm rate* is not clearly defined.

How to Compute the False Alarm Rate ?
-------------------------------------
There are two competing definitions for the *false alarm rate*:
the *False Positive Rate (FPR)*, the most commonly used, and the
*False Discovery Rate (FDR)*:

* :math:`FPR = \frac{FP}{FP + TN}`

* :math:`FDR = \frac{FP}{FP + TP}`.

The FPR is the proportion of benign instances that have triggered a false
alarm, while the FDR measures the proportion of the alerts that are irrelevant.

The FDR makes more sense than the FPR from an operational point of view.
First of all, it can be computed in operational environments in contrast
to the FPR (the number of benign instances, :math:`FP + TN`, is unknown in practice).
Moreover, the FDR reveals the proportion of security operators' time wasted
analyzing meaningless alerts, while the FPR has no tangible interpretation.
Finally, the FPR can be highly misleading when the proportion of malicious
instances is extremely low because of the base-rate fallacy.
Let's take an example.
We consider 10,000 instances (10 malicious and 9990 benign) and we suppose
that there are 10 false positives and 2 false negatives
(:math:`FP = 10`, :math:`FN = 2`, :math:`TP = 8`, :math:`TN = 9980`).
In this case, the FPR seems negligible (:math:`FPR = 0.1\%`)
while security operators spend more than half of their reviewing time analyzing
meaningless alerts (:math:`FDR = 55\%`).

For all these reasons, the False Discovery Rate (FDR) should be preferred
over the False Positive Rate (FPR) even if it is still less prevalent in
practice.

.. note::

  In SecuML the False Alarm Rate (FAR) corresponds to the
  False Discovery Rate (FDR).


ROC and FAR-DR Curves
----------------------
The measures of performance we have introduced so far depend on the value of
the detection threshold.
The ROC (Receiver Operating Characteristic) is another measure of performance.
It has the benefit of being independent of the detection threshold.
This curve represents the detection rate according to the false positive rate
for various values of the detection threshold.

.. figure:: figs/detection_perf_metrics/roc_explanation.svg
  :width: 70%
  :align: center

  Explanation of the ROC Curve.


For a threshold of :math:`100\%`, the detection and false alarm rates are null,
and for a threshold of :math:`0\%` they are both equal to :math:`100\%`.
A good detection model has a ROC curve close to the upper left corner : a high
detection rate with a low false alarm rate.
The AUC, which stands for Area Under the ROC Curve, is often computed to assess
the performance of a detection model independently of the detection threshold.
A good detection model has an AUC close to :math:`100\%`.

The ROC curve of a classifier predicting randomly the probability of
maliciousness  is the straight red line.
A ROC curve is always above this straight line and the AUC is at least
:math:`50\%`.
Thanks to the ROC curve, we can set the value of the  detection threshold
according to the detection rate desired or the false alarm rate tolerated.

.. note::

  The ROC curve is interesting to check whether machine learning has learned
  something from the data, i.e. the ROC curve is away from those of a random
  generator.
  However, the False Alarm Rate - Detection Rate (FAR-DR) curve must be
  preferred to set the value of the detection threshold according to the
  desired detection rate or the tolerated FAR (FDR),
  for the same reason that the FDR should be preferred over the FPR.
