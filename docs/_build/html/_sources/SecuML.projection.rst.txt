Projection
===========

The data are projected into a lower-dimensional space for visualization. The user interface allows to display the instances in a plane defined by two components.
The instances are not displayed individually but with an hexagonal binning (color from green to black according to the number of instances in the bin).
The color of the dot in the middle of each bin (from yellow to red) corresponds to the proportion of known malicious instances in the bin.

.. code-block:: bash

    SecuML_projection <project> <dataset> <algo>

*Help*

For more information about the available options for a given projection algorithm:

.. code-block:: bash

    SecuML_projection <project> <dataset> <algo> -h

Algorithms Available
---------------------

+ Unsupervised Algorithms
    + Pca

+ Semi-supervised Algorithms
    + Rca
    + Lda
    + Lmnn
    + Nca
    + Itml


Graphical User Interface
------------------------

.. figure:: screen_shots/projection/main.png

    Projection Interface
