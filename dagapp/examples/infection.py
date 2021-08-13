"""Simple model relating vaccination to death toll, involving exposure and infection rate
                        ┌──────────────────────┐
                        │   death_vax_factor   │
                        └──────────────────────┘
                          │
                          ▼
┌─────────────────┐     ┌──────────────────────────────────┐
│ die_if_infected │ ──▶ │               die                │
└─────────────────┘     └──────────────────────────────────┘
                          │                       ▲    ▲
                          ▼                       │    │
┌─────────────────┐     ┌──────────────────────┐  │  ┌─────┐
│   population    │ ──▶ │      death_toll      │  │  │ vax │
└─────────────────┘     └──────────────────────┘  │  └─────┘
                                                  │    │
                        ┌──────────────────────┐  │    │
                        │ infection_vax_factor │  │    │
                        └──────────────────────┘  │    │
                          │                       │    │
                          ▼                       │    │
                        ┌──────────────────────┐  │    │
                     ┌▶ │       infected       │ ─┘    │
                     │  └──────────────────────┘       │
                     │    ▲                            │
                     │    └────────────────────────────┘
                     │  ┌──────────────────────┐
                     │  │       exposed        │
                     │  └──────────────────────┘
                     │    │
                     │    ▼
                     │  ┌──────────────────────┐
                     └─ │          r           │
                        └──────────────────────┘
                          ▲
                          │
                        ┌──────────────────────┐
                        │   infect_if_expose   │
                        └──────────────────────┘
"""

from meshed.dag import DAG
from functools import partial
from dagapp.page_funcs import StaticPageFunc
from dagapp.base import dag_app

from meshed.examples.vaccine_vs_no_vaccine import *

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
