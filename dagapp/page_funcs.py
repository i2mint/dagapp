import streamlit as st
from i2 import Sig
from dagapp.utils import (
    get_values,
    get_funcs,
    get_nodes,
    display_factory,
    binary_classification_factory,
)


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


class BinaryClassificationPageFunc(BasePageFunc):
    def __call__(self):
        if self.page_title:
            st.markdown(f"""## **{self.page_title}**""")

        c1, c2 = st.beta_columns(2)

        c2.graphviz_chart(self.dag.dot_digraph())
        funcs = get_funcs(self.dag)
        nodes = get_nodes(self.dag)
        values = get_values(self.dag, funcs)
        arg_types = self.configs["arg_types"]

        binary_classification_factory(self.dag, nodes, funcs, values, arg_types, c1)
