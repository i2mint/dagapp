"""A simple example of making an app from DAGs"""

from dagapp.base import dag_app
from meshed.dag import DAG
from functools import partial


def b(a):
    return 2 ** a


def d(c):
    return 10 - (5 ** c)


def result(b, d):
    return b * d


dags = [
    DAG((b, d, result)),
]

if __name__ == '__main__':
    app = partial(dag_app, dags=dags)
    app()
