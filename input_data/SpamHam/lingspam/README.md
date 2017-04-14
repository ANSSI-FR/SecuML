# Lingspam Dataset

This dataset provides an example of how the data should be formatted to run experiments with SecuML. This labeled dataset for spam detection has been built from the raw email dataset lingspam (see [ling-spam-datasets.html](http://csmining.org/index.php/ling-spam-datasets.html)).

In order to display the raw email messages in the web user interface you must first download the raw data with the script `download_lingpam_data`.

Each email message is described by 1000 boolean features representing whether a word a present or not in the message. The words considered are the 1000 most present in all the messages.

The original lingspam dataset does not provide families. We have performed a clustering on the malicious and benign instances separately,
to assign a family to each instance.
