"""A dagapp to make binary classifier metrics"""

from collections import Counter
import numpy as np


def _aligned_items(a, b):
    """Yield (k, a_value, b_value) triples for all k that are both a key of a and of b"""
    # reason for casting to dict is to make sure things like pd.Series use the right
    # keys.
    # could also use k in a.keys() etc. to solve this.
    a = dict(a)
    b = dict(b)
    for k in a:
        if k in b:
            yield k, a[k], b[k]


def _dot_product(a, b):
    """
    >>> dot_product({'a': 1, 'b': 2, 'c': 3}, {'b': 4, 'c': -1, 'd': 'whatever'})
    5
    """
    return sum(ak * bk for _, ak, bk in _aligned_items(a, b))


def classifier_score(confusion_count, confusion_value):
    """Compute a score for a classifier that produced the `confusion_count`, based on
    the given `confusion_value`.
    Meant to be curried by fixing the confusion_value dict.

    The function is purposely general -- it is not specific to binary classifier
    outcomes, or even any classifier outcomes.
    It simply computes a normalized dot product, depending on the inputs keys to align
    values to multiply and
    considering a missing key as an expression of a null value.
    """
    return _dot_product(confusion_count, confusion_value) / sum(confusion_count.values())


def confusion_count(prediction, truth):
    """Get a dict containing the counts of all combinations of predicction and
    corresponding truth values.

    >>> confusion_count(
    ... [0, 0, 1, 0, 1, 1, 1],
    ... [0, 0, 0, 1, 1, 1, 1]
    ... )
    Counter({(0, 0): 2, (1, 0): 1, (0, 1): 1, (1, 1): 3})
    """
    return Counter(zip(prediction, truth))


def prediction(predict_proba, threshold):
    """Get an array of predictions from thresholding the scores of predict_proba array.

    >>> prediction([0.3, 0.4, 0.5, 0.6, 0.7, 0.8], threshold=0.5)
    array([False, False,  True,  True,  True,  True])

    """
    return np.array(predict_proba) >= threshold


def predict_proba(model, test_X):
    """Get the prediction_proba scores of a model given some test data"""
    return model.predict_proba(test_X)
