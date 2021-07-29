"""The base components for making apps from DAGs"""

import streamlit as st
from i2 import Sig
from dagapp.utils import get_values, get_funcs, get_nodes, check_configs


def display_factory(dag, nodes, funcs, values, slider, ranges, col):
    with col:
        for node in nodes:
            kwargs = dict(
                value=values[node],
                on_change=update_nodes,
                args=(dag, funcs),
                key=node,
            )
            if slider:
                kwargs["min_value"] = ranges[node][0]
                kwargs["max_value"] = ranges[node][1]
                st.slider(node, **kwargs)
            else:
                st.number_input(node, **kwargs)


def update_nodes(dag, funcs):
    for node in dag.var_nodes:
        if node not in dag.roots:
            args = [st.session_state[arg] for arg in list(funcs[node].src_names.keys())]
            st.session_state[node] = funcs[node].func(*args)


class BasePageFunc:
    def __init__(self, dag, page_title: str = "", **config):
        self.dag = dag
        self.page_title = page_title
        self.sig = Sig(dag)
        self.configs = config

    def __call__(self):
        if self.page_title:
            st.markdown(f"""## **{self.page_title}**""")
        st.write(Sig(self.dag))


class SimplePageFunc(BasePageFunc):
    def __call__(self):
        if self.page_title:
            st.markdown(f"""## **{self.page_title}**""")

        c1, c2 = st.beta_columns(2)

        c2.graphviz_chart(self.dag.dot_digraph())

        funcs = get_funcs(self.dag)
        nodes = get_nodes(self.dag)
        values = get_values(self.dag, funcs)

        if self.configs["slider"]:
            ranges = self.configs["ranges"]
            display_factory(self.dag, nodes, funcs, values, True, ranges, c1)
        else:
            display_factory(self.dag, nodes, funcs, values, False, None, c1)


def dag_to_page_name(dag):
    return f"{list(dag.leafs)[0].capitalize()} Calculator"


def get_page_callbacks(dags, page_names, configs):
    return [
        SimplePageFunc(dag, page_name, **config)
        for dag, page_name, config in zip(dags, page_names, configs)
    ]


def get_pages_specs(dags, configs):
    page_names = [dag_to_page_name(dag) for dag in dags]
    page_callbacks = get_page_callbacks(dags, page_names, configs)
    return dict(zip(page_names, page_callbacks))


def dag_app(dags, configs=None):
    if configs is None:
        configs = [{"slider": False} for _ in range(len(dags))]

    check_configs(dags, configs)

    st.set_page_config(layout="wide")

    pages = get_pages_specs(dags, configs)

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select your page", tuple(pages.keys()))

    pages[page]()
