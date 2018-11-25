function interactiveAnnotations() {
    if (train_test == 'validation') {
        return false;
    } else {
        return !(inst_annotations_type == 'ground_truth');
    }
}
