"""An example of making an app from DAGs with configs defined"""

from dagapp.base import dag_app
from meshed.dag import DAG
from functools import partial
from dagapp.page_funcs import StaticPageFunc

DFLT_VAX = 0.5


def _factor(vax, vax_factor):
    assert 0 <= vax <= 1, 'vax should be between 0 and 1: Was {vax}'
    return vax * vax_factor + (1 - vax)


def r(exposed: float = 6, infect_if_expose: float = 1 / 5):
    return exposed * infect_if_expose


def infected(r: float = 1.2, vax: float = DFLT_VAX, infection_vax_factor: float = 0.15):
    return r * _factor(vax, infection_vax_factor)


def die(
    infected: float,
    die_if_infected: float = 0.05,
    vax: float = DFLT_VAX,
    death_vax_factor: float = 0.05,
):
    return infected * die_if_infected * _factor(vax, death_vax_factor)


def death_toll(die: float, population: int = 1e6):
    return int(die * population)


# def infected(exposed=6, infect_if_exposed=1 / 5, vax=True, infection_vax_factor=0.15):
#     return exposed * infect_if_exposed * _factor(vax, infection_vax_factor)
#
#
# def die(infected, die_if_infected=0.05, vax=True, death_vax_factor=0.05):
#     return infected * die_if_infected * _factor(vax, death_vax_factor)


dags = [
    DAG((r, infected, die, death_toll)),
]

from i2 import Sig

num_fields = {*Sig(r).names, *Sig(infected).names, *Sig(die).names} - {'vax'}

configs = [
    dict(
        arg_types=dict(
            infect_if_exposed='num',
            infected='num',
            die_if_infected='num',
            death_vax_factor='num',
            exposed='num',
            vax='num',
            infect_if_expose='num',
            infection_vax_factor='num',
            population='num',
        ),
    ),
    # dict(
    #     arg_types=dict(
    #         infect_if_exposed='slider',
    #         infected='slider',
    #         die_if_infected='slider',
    #         death_vax_factor='slider',
    #         exposed='slider',
    #         # vax='slider',
    #         infect_if_expose='slider',
    #         infection_vax_factor='slider',
    #     ),
    #     ranges=dict(
    #         infect_if_exposed=[0, 1.0],
    #         infected=[0, 1.0],
    #         die_if_infected=[0, 1.0],
    #         death_vax_factor=[0, 1.0],
    #         exposed=[0, 1.0],
    #         # vax=[0, 1.0],
    #         infect_if_expose=[0, 1.0],
    #         infection_vax_factor=[0, 1.0],
    #     ),
    # ),
]

if __name__ == '__main__':
    app = partial(dag_app, dags=dags, page_factory=StaticPageFunc, configs=configs)
    app()
