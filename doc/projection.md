# Projecting Data

The data are projected into a lower-dimensional space for visualization. The user interface allows to display the instances in a plane defined by two components.
The instances are not displayed individually but with an hexagonal binning (color from green to black according to the number of instances in the bin).
The color of the dot in the middle of each bin (from yellow to red) corresponds to the proportion of known malicious instances in the bin.

    ./SecuML_projection <project> <dataset> -f <features_files> --algo <Pca/Lda/Lmnn>

For more information about the available options:

    ./SecuML_projection -h

Web interface to display the results:

    http://localhost:5000/SecuML/<project>/<dataset>/Projection/menu/

## Interface
![Projection](/doc/images/projection.png)
