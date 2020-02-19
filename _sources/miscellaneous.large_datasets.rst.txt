.. _misc_large_datasets:

Running SecuML on Large Datasets
================================

The following tips allow to run SecuML on large datasets.

Storing Features as Sparse Matrices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SecuML supports sparse
feature matrices  for some types of experiments.
CSC, CSR and LIL
`scipy sparse formats <https://scikit-learn.org/stable/developers/performance.html>`_
are supported (see :ref:`Data<Data>`).

:ref:`Clustering <clustering>` and :ref:`Projection <projection>`
do not support sparse matrices.
:ref:`Features Analysis <stats>` supports sparse matrices and
the CSC format should be preferred for maximum efficiency.

Regarding :ref:`DIADEM <DIADEM>` and :ref:`ILAB <ILAB>`, it depends on the
selected model class. SecuML relies on scikit-learn learning algorithms
and some of them do not support sparse matrices.
You must then refer to the scikit-learn documentation to check whether
a given model class can be trained from sparse features and to know
the best suited sparse format for maximum efficency.

Proving the Features' Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The types of the features can be provided in a
:ref:`description file <features_description_file>`
to load the dataset more quickly.
When the features' types are provided, SecuML does not need to infer them.


Reducing the Number of Parallel Jobs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Various experiments can be parallelized with the ``--n-jobs`` argument.
Reducing the number of jobs allows to decrease the memory usage.

Streaming Validation
^^^^^^^^^^^^^^^^^^^^
Detection models trained with :ref:`DIADEM <DIADEM>` can be tested
on a validation dataset in streaming thanks to the arguments
``--validation-mode ValidationDatasets --validation-datasets <validation_datasets> --streaming``.
This way the validation instances are not loaded into memory at once which
allows to process bigger datasets.

.. note::

   Scipy sparse matrices cannot be processed in streaming.

Selecting an Appropriate Optimization Algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Logistic regression can be trained with various optimization algorithms
(``liblinear``, ``lbfgs``, ``sag``, and ``saga``).
By default, SecuML trains logistic regression models with ``liblinear``
which suits small datasets.
``sag`` and ``saga`` are more suitable for large datasets.
