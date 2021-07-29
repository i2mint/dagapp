"""A simple example of making an app from DAGs"""

from dagapp.base import dag_app
from meshed.dag import DAG
from functools import partial


def thing1(a, b):
    return a + b


def thing2(c, d):
    return c - d


def result(thing1, thing2):
    return thing1 * thing2


dags = [
    DAG((thing1, thing2, result)),
]

if __name__ == "__main__":
    app = partial(dag_app, dags=dags)
    app()
