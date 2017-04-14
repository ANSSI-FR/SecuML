# Training and Analysing a Detection Model before Deployment

A supervised detection model is learned from a labelled dataset, and applied to a validation dataset (labelled or not).
The GUI displays performance indicators (detection rate, false alarm rate, f-score, ROC, AUC, confusion matrix, ...) of the detection model on the training dataset and on the validation dataset (if ground truth labels are available).
The false positives and negatives can be displayed from the confusion matrix.
The GUI also allows to analyse the alerts raised on the validation dataset (the top N alerts, randomly selected alerts, or a clustering of the alerts).

    ./SecuML_classification <project> <dataset> -f <features_files>
    ./SecuML_classification <project> <dataset> -f <features_files> --validation-dataset <validation_dataset>

For more information about the available options:

	./SecuML_classification -h

Web interface to display the results:

	http://localhost:5000/SecuML/<project>/<dataset>/Classification/menu/


## Monitoring Interface
![Classification](/doc/images/classification.png)
