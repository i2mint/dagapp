"""The base components for making apps from DAGs"""

import streamlit as st
from i2 import Sig

dflt_type = {int: 0, float: 0.0}


def infer_default(dag, name):
    if name in dag.leafs:
        return 0

    for func_node in dag.func_nodes:
        if name in func_node.sig.defaults:
            dflt = func_node.sig.defaults[name]
            if dflt is not None:
                return dflt
        elif name in func_node.sig.annotations:
            return dflt_type[func_node.sig.annotations[name]]


def get_funcs(dag):
    funcs = dict()
    for func_node in dag.func_nodes:
        funcs[func_node.name[:-1]] = func_node
    return funcs


def get_nodes(dag):
    nodes = dag.sig.names
    for node in dag.nodes:
        if node not in nodes and isinstance(node, str):
            nodes.append(node)
    return nodes


def display_factory(nodes, dag, funcs, col):
    for node in nodes:
        with col:
            st.number_input(
                node,
                value=infer_default(dag, node),
                on_change=update_nodes,
                args=(
                    dag,
                    funcs,
                ),
                key=node,
            )


def update_nodes(dag, funcs):
    for node in dag.var_nodes:
        if node not in dag.roots:
            args = [st.session_state[arg] for arg in list(funcs[node].src_names.keys())]
            st.session_state[node] = funcs[node].func(*args)


class BasePageFunc:
    def __init__(self, dag, page_title: str = ""):
        self.dag = dag
        self.page_title = page_title
        self.sig = Sig(dag)

    def __call__(self):
        if self.page_title:
            st.markdown(f"""## **{self.page_title}**""")
        st.write(Sig(self.func))


class SimplePageFunc(BasePageFunc):
    def __call__(self):
        if self.page_title:
            st.markdown(f"""## **{self.page_title}**""")

        c1, c2 = st.beta_columns(2)

        c2.graphviz_chart(self.dag.dot_digraph())

        funcs = get_funcs(self.dag)
        nodes = get_nodes(self.dag)

        display_factory(nodes, self.dag, funcs, c1)


def dag_to_page_name(dag):
    return f"{list(dag.leafs)[0].capitalize()} Calculator"


def get_page_callbacks(dags, page_names):
    return [SimplePageFunc(dag, page_name) for dag, page_name in zip(dags, page_names)]


def get_pages_specs(dags):
    page_names = [dag_to_page_name(dag) for dag in dags]
    page_callbacks = get_page_callbacks(dags, page_names)
    return dict(zip(page_names, page_callbacks))


def dag_app(dags):
    st.set_page_config(layout="wide")

    pages = get_pages_specs(dags)

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select your page", tuple(pages.keys()))

    pages[page]()
