"""Different page functions used to turn dags to app"""

import streamlit as st
from i2 import Sig
from dagapp.utils import (
    get_values,
    get_funcs,
    get_nodes,
    display_factory,
    get_from_configs,
    static_factory,
    vector_factory,
)


class BasePageFunc:
    def __init__(self, dag, page_title: str = '', **config):
        self.dag = dag
        self.page_title = page_title
        self.sig = Sig(dag)
        self.configs = config

    def __call__(self):
        if self.page_title:
            st.markdown(f'''## **{self.page_title}**''')
        st.write(Sig(self.dag))


class SimplePageFunc(BasePageFunc):
    def __call__(self):
        if self.page_title:
            st.markdown(f'''## **{self.page_title}**''')

        c1, c2 = st.columns(2)

        c2.graphviz_chart(self.dag.dot_digraph())

        funcs = get_funcs(self.dag)
        nodes = get_nodes(self.dag)
        values = get_values(self.dag, funcs)
        arg_types, ranges = get_from_configs(self.configs)

        display_factory(self.dag, nodes, funcs, values, arg_types, ranges, c1)


class StaticPageFunc(BasePageFunc):
    def __call__(self):
        if self.page_title:
            st.markdown(f'''## **{self.page_title}**''')

        c1, c2 = st.columns(2)

        c2.graphviz_chart(self.dag.dot_digraph())
        funcs = get_funcs(self.dag)
        nodes = get_nodes(self.dag)
        values = get_values(self.dag, funcs)
        arg_types, ranges = get_from_configs(self.configs)

        static_factory(self.dag, nodes, funcs, values, arg_types, ranges, c1)


class VectorizePageFunc(BasePageFunc):
    def __call__(self):
        if self.page_title:
            st.markdown(f'''## **{self.page_title}**''')

        c1, c2 = st.columns(2)

        c2.graphviz_chart(self.dag.dot_digraph())
        funcs = get_funcs(self.dag)
        nodes = get_nodes(self.dag)
        # values = get_values(self.dag, funcs)
        # arg_types, ranges = get_from_configs(self.configs)

        vector_factory(self.dag, nodes, funcs, c1)
