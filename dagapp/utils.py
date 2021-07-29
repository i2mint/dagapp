"""Utils"""

import streamlit as st

DFLT_VALS = {int: 0, float: 0.0}


def get_values(dag, funcs):
    defaults = dict()
    for name in dag.sig.names:
        if name in dag.sig.defaults:
            dflt = dag.sig.defaults[name]
            if dflt is not None:
                defaults[name] = dflt
        elif name in dag.sig.annotations:
            defaults[name] = DFLT_VALS[dag.sig.annotations[name]]
        else:
            defaults[name] = 0.0

    for name in funcs:
        func_node = funcs[name]
        if set(func_node.sig.names).issubset(set(list(defaults.keys()))):
            kwargs = dict()
            for arg_name in func_node.sig.names:
                kwargs[arg_name] = defaults[arg_name]
            defaults[name] = func_node.func(**kwargs)

    return defaults


def get_nodes(dag):
    nodes = dag.sig.names
    for node in dag.nodes:
        if node not in nodes and isinstance(node, str):
            nodes.append(node)
    return nodes


def get_funcs(dag):
    funcs = dict()
    for func_node in dag.func_nodes:
        funcs[func_node.name[:-1]] = func_node
    return funcs


def check_configs(dags, configs):
    if len(configs) != len(dags):
        st_error("You need to define configs for all of your DAGs!")

    for dag, config in zip(dags, configs):
        if "slider" not in config:
            st_error("You need to define if you want slider or number input in your configs!")
        elif config['slider']:
            if 'ranges' not in config:
                st_error("You need to define your slider ranges if you want sliders!")
            else:
                if not isinstance(config['ranges'], dict):
                    st_error("You need to define your slider ranges as a dictionary of two-element lists!")
                elif not set(get_nodes(dag)).issubset(set(config['ranges'].keys())):
                    st_error("You need to define a slider range for every component of your DAG!")


def st_error(message):
    st.error(message)
    st.stop()


def infer_default(dag, name, funcs):
    if name not in dag.sig.names:
        func_node = funcs[name]
        if len(func_node.sig.defaults) == len(func_node.sig.params):
            return func_node.func()
        else:
            kwargs = dict()
            for arg_name in func_node.sig.names:
                if arg_name in funcs:
                    if len(funcs[arg_name].sig.defaults) == len(
                        funcs[arg_name].sig.params
                    ):
                        kwargs[arg_name] = funcs[arg_name].func()
                elif arg_name in func_node.sig.defaults:
                    dflt = func_node.sig.defaults[arg_name]
                    if dflt is not None:
                        kwargs[arg_name] = dflt
            if len(kwargs) == len(func_node.sig.params):
                return func_node.func(**kwargs)

    for func_node in dag.func_nodes:
        if name in func_node.sig.defaults:
            dflt = func_node.sig.defaults[name]
            if dflt is not None:
                return dflt
        elif name in func_node.sig.annotations:
            return DFLT_VALS[func_node.sig.annotations[name]]

    if name in dag.leafs:
        if len(dag.sig.defaults) == len(dag.sig.params):
            return dag()

    return 0.0
