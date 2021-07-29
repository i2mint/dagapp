"""A simple example of making a app from DAGs"""

from dagapp.base import dag_app
from meshed.dag import DAG
from functools import partial


# def clicks(click_thru_rate, impressions):
#     return impressions * click_thru_rate
#
#
# def sales(clicks, conversion_rate):
#     return clicks * conversion_rate


def partners(maxPartners: int, cpc: float = 0.2, priceElasticity: int = 120):
    return int(maxPartners - cpc * priceElasticity)


def clicks(partners: int, cpp: float):
    return int(partners * cpp)


def revenue(clicks: int, cpc: float = 0.2):
    return clicks * cpc


def user_clicks(a: int = 100, b: int = 3, cpc: float = 0.1):
    return a * (b ** cpc)


def rev(user_clicks: float, rpc: int = 2):
    return user_clicks * rpc


def cost(user_clicks: float, cpc: float = 0.1):
    return cpc * user_clicks


def profit(cost: float, rev: float):
    return rev - cost


dags = [DAG((partners, clicks, revenue)), DAG((user_clicks, rev, cost, profit))]

if __name__ == "__main__":
    app = partial(dag_app, dags=dags)
    app()
