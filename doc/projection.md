# Projecting Data

The data are projected into a lower-dimensional space for visualization. The user interface allows to display the instances in a plane defined by two components.
The instances are not displayed individually but with an hexagonal binning (color from green to black according to the number of instances in the bin).
The color of the dot in the middle of each bin (from yellow to red) corresponds to the proportion of known malicious instances in the bin.

    ./SecuML_projection <algo> <project> <dataset> -f <features_files>

To display the available projection algorithms:

    ./SecuML_projection -h

For more information about the available options for a given projection algorithm:

    ./SecuML_projection <algo> -h

Web interface to display the results:

    http://localhost:5000/SecuML/<project>/<dataset>/Projection/menu/

## Interface
![Projection](/doc/images/projection.png)
