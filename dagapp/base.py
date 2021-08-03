"""The base components for making apps from DAGs"""

import streamlit as st
from dagapp.utils import check_configs, get_default_configs
from dagapp.page_funcs import SimplePageFunc


def dag_to_page_name(dag):
    return f'{list(dag.leafs)[0].capitalize()} Calculator'


def get_page_callbacks(dags, page_names, page_factory, configs):
    return [
        page_factory(dag, page_name, **config)
        for dag, page_name, config in zip(dags, page_names, configs)
    ]


def get_pages_specs(dags, page_factory, configs):
    page_names = [dag_to_page_name(dag) for dag in dags]
    page_callbacks = get_page_callbacks(dags, page_names, page_factory, configs)
    return dict(zip(page_names, page_callbacks))


def dag_app(dags, page_factory=SimplePageFunc, configs=None):
    if configs is None:
        configs = get_default_configs(dags)

    check_configs(dags, configs)

    # st.set_page_config(layout="wide")

    pages = get_pages_specs(dags, page_factory, configs)

    st.sidebar.title('Navigation')
    page = st.sidebar.radio('Select your page', tuple(pages.keys()))

    pages[page]()
