"""An example of vectorizing inputs with DAGs"""

from dagapp.base import dag_app
from meshed.dag import DAG
from functools import partial
from dagapp.page_funcs import VectorizePageFunc


def b(a):
    return 2 ** a


def d(c):
    return 10 - (5 ** c)


def result(b, d):
    return b * d


dags = [
    DAG((b, d, result)),
]

if __name__ == "__main__":
    app = partial(dag_app, dags=dags, page_factory=VectorizePageFunc)
    app()
