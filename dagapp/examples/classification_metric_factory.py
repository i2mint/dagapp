"""A dagapp to make binary classifier metrics"""

from collections import Counter
import numpy as np
from functools import partial
from typing import Mapping, Iterable

from meshed.dag import DAG
from dagapp.base import dag_app


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
    >>> _dot_product({'a': 1, 'b': 2, 'c': 3}, {'b': 4, 'c': -1, 'd': 'whatever'})
    5
    """
    return sum(ak * bk for _, ak, bk in _aligned_items(a, b))


def classifier_score(
    confusion_count: Mapping[str, int], confusion_value: Mapping[str, int]
):
    """Compute a score for a classifier that produced the `confusion_count`, based on
    the given `confusion_value`.
    Meant to be curried by fixing the confusion_value dict.

    The function is purposely general -- it is not specific to binary classifier
    outcomes, or even any classifier outcomes.
    It simply computes a normalized dot product, depending on the inputs keys to align
    values to multiply and
    considering a missing key as an expression of a null value.
    """
    return _dot_product(confusion_count, confusion_value) / sum(
        confusion_count.values()
    )


def confusion_count(prediction: Iterable[int], truth: Iterable[int], positive: int = 1):
    """Get a dict containing the counts of all combinations of prediction and
    corresponding truth values.

    >>> confusion_count(
    ... [0, 0, 1, 0, 1, 1, 1],
    ... [0, 0, 0, 1, 1, 1, 1]
    ... )
    {'tn': 2, 'fp': 1, 'fn': 1, 'tp': 3}
    """
    confusion = dict(Counter(zip(prediction, truth)))
    keys = list(confusion.keys())
    for key in keys:
        if key[0] == key[1]:
            if key[1] == positive:
                confusion['tp'] = confusion[key]
            else:
                confusion['tn'] = confusion[key]
        else:
            if key[1] == positive:
                confusion['fn'] = confusion[key]
            else:
                confusion['fp'] = confusion[key]
        del confusion[key]

    keys = [key for key in ['tp', 'tn', 'fn', 'fp'] if key not in confusion.keys()]
    for key in keys:
        confusion[key] = 0

    return confusion


def prediction(predict_proba, threshold):
    """Get an array of predictions from thresholding the scores of predict_proba array.

    >>> prediction([0.3, 0.4, 0.5, 0.6, 0.7, 0.8], threshold=0.5)
    array([False, False,  True,  True,  True,  True])
    """
    return np.array(predict_proba) >= threshold


def predict_proba(model, test_X):
    """Get the prediction_proba scores of a model given some test data"""
    return model.predict_proba(test_X)


dags = [DAG((confusion_count, classifier_score))]
configs = [
    dict(
        arg_types=dict(
            prediction='list', truth='list', positive='num', confusion_value='dict',
        ),
    )
]

if __name__ == '__main__':
    app = partial(dag_app, dags=dags, configs=configs)
    app()
