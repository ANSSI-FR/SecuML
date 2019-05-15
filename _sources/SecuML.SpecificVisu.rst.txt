.. _instance-visu:

Visualization of Individual Instances
=====================================

SecuML web user interface displays individual instances (e.g. errors from the
confusion matrix with DIADEM, or instances to annotate with ILAB) in a
*Description* panel.

Default Visualization: All the Features
-----------------------------------------
By default, the *Description* panel displays the values of all the features
of the instance.
:ref:`all-features` displays the features extracted from an email
in the :ref:`spam detection use case<lingspam-use-case>`:
the number of occurrences of each word in the vocabulary.
Since the vocabulary contains 1000 words, this visualization is hardly
interpretable for humans.

.. _all-features:

.. figure:: figs/screen_shots/DIADEM/features_values.png
  :width: 80%
  :align: center

  All the Features for Spam Detection

.. _problem-specific-visu:

Pluggable Problem-Specific Visualizations
-----------------------------------------
SecuML enables to plug problem-specific visualizations for each project
(the datasets belonging to the same project share the same problem-specific
visualizations).
:ref:`mail-specific-visu` depicts a problem-specific visualization
we have implemented for the :ref:`spam detection use case<lingspam-use-case>`.
It simply displays the raw content of the email message, but
it is much easier to analyze than :ref:`all-features`.

.. _mail-specific-visu:

.. figure:: figs/screen_shots/DIADEM/mail.png
  :width: 80%
  :align: center

  Mail Visualization for Spam Detection

Problem-specific visualizations should be easily interpretable by security
experts and display the most relevant elements from a detection perspective.
They may point out to external tools or information to provide some context.
Several custom visualizations can be implemented (in different tabs) to show
the instances from various angles.

.. note::

  Problem-specific visualizations are not required to use SecuML web user
  interface. However, we strongly encourage to implement convenient
  problem-specific visualizations, since they can significantly ease the
  analysis of individual instances.

  Moreover, all SecuML modules (e.g. :ref:`DIADEM<DIADEM>`,
  :ref:`ILAB<ILAB>`, :ref:`projection`, :ref:`clustering`)
  rely one the same *Description* panel to display the instances.
  As a result, once a custom visualization has been implemented for a given
  project it is displayed by all SecuML modules.


Implementation
^^^^^^^^^^^^^^^

JavaScript code
"""""""""""""""
| The code must be stored in ``secuml/web/static/js/instances_visu/<project>.js``.
| See `secuml/web/static/js/instances_visu/SpamHam.js <https://github.com/ANSSI-FR/SecuML/blob/master/secuml/web/static/js/instances_visu/SpamHam.js>`_ for an example.

Flask code
""""""""""
| The code must be stored in ``secuml/web/views/projects/<project>.py``.
| See `secuml/web/views/projects/SpamHam.py <https://github.com/ANSSI-FR/SecuML/blob/master/secuml/web/views/projects/SpamHam.py>`_ for an example.
