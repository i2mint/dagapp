"""An example of making an app from DAGs with configs defined"""

from dagapp.base import dag_app
from meshed.dag import DAG
from functools import partial
from dagapp.page_funcs import StaticPageFunc


def partners(
    max_partners: int, cost_per_click: float = 0.2, price_elasticity: int = 120
):
    return int(max_partners - cost_per_click * price_elasticity)


def clicks(partners: int, clicks_per_partner: float):
    return int(partners * clicks_per_partner)


def revenue(clicks: int, cost_per_click: float = 0.2):
    return clicks * cost_per_click


def user_clicks(a: int = 100, b: int = 3, cost_per_click: float = 0.1):
    return a * (b ** cost_per_click)


def rev(user_clicks: float, revenue_per_click: int = 2):
    return user_clicks * revenue_per_click


def cost(user_clicks: float, cost_per_click: float = 0.1):
    return cost_per_click * user_clicks


def profit(cost: float, rev: float):
    return rev - cost


dags = [
    DAG((user_clicks, rev, cost, profit)),
    DAG((partners, clicks, revenue)),
]

configs = [
    dict(
        arg_types=dict(
            a='num', b='num', cost_per_click='num', revenue_per_click='num',
        ),
    ),
    dict(
        arg_types=dict(
            max_partners='slider',
            cost_per_click='slider',
            price_elasticity='slider',
            partners='slider',
            clicks_per_partner='slider',
        ),
        ranges=dict(
            max_partners=[0, 2000],
            cost_per_click=[0.0, 1.0],
            price_elasticity=[0, 200],
            partners=[0, 1500],
            clicks_per_partner=[0.0, 10.0],
            # clicks=[0, 100000],
            # revenue=[0.0, 1000000.0],
        ),
    ),
]

if __name__ == '__main__':
    app = partial(dag_app, dags=dags, page_factory=StaticPageFunc, configs=configs)
    app()
