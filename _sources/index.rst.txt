.. SecuML documentation master file, created by
   sphinx-quickstart on Tue Jun 12 14:54:29 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SecuML's documentation
======================

SecuML is a Python tool that aims to foster the use of machine learning in computer security.
It is distributed under the GPL2+ license.

It allows to apply diverse machine learning techniques
(e.g. supervised learning, active learning, rare category detection, clustering).
It does not propose new implementations of machine learning algorithms.
It is built upon third-party libraries
(`scikit-learn <http://scikit-learn.org/>`_ and `metric-learn <https://github.com/metric-learn/metric-learn/tree/master/doc>`_),
and offers additionnal features:
it comes with a graphical user interface and
it hides some of the machine learning machinery to let security experts focus mainly on detection.

**Graphical User Interface.**
It visualizes the results of the machine learning analyses
and allows to interact with the models (e.g. active learning, rare category detection).
It is generic and can be used on any data type thanks to the pluggable
:ref:`problem-specific visualizations <problem-specific-visu>`.

**Hiding some of the Machine Learning Machinery.**
SecuML deals with data loading and performs automatically
some parts of the machine learning pipeline (e.g. feature standardization, search of the best hyperparameters)
to let security experts focus mainly on detection.

.. toctree::
  :maxdepth: 2
  :caption: Getting Started

  getting_started.setting_up
  getting_started.lingspam

.. toctree::
  :maxdepth: 2
  :caption: Data and Experiments

  SecuML.Data
  SecuML.SpecificVisu
  SecuML.Experiments

.. toctree::
  :maxdepth: 1
  :caption: Available Experiments

  SecuML.DIADEM
  SecuML.ILAB
  SecuML.RCD
  SecuML.clustering
  SecuML.projection
  SecuML.stats

.. toctree::
  :maxdepth: 1
  :caption: Miscellaneous

  miscellaneous.detection_perf.rst
  miscellaneous.large_datasets.rst

.. Indices and tables
.. ==================
..
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
