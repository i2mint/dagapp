"""Utils"""

import streamlit as st
from typing import Mapping, Iterable, Any

DFLT_VALS = {
    int: 0,
    float: 0.0,
    Iterable[int]: "0,0,0,0",
    Mapping[str, int]: dict(tp=0, fn=0, fp=0, tn=0),
}

WIDGET_TYPE = {
    "num": st.number_input,
    "slider": st.slider,
    "string": st.text_input,
    "dict": st.text_input,
}

ARG_WIDGET_MAP = {
    "num": st.number_input,
    "slider": st.slider,
    "list": st.text_input,
    "dict": st.beta_expander,
}


# ------------------------------------ BINARY CLASSIFICATION ------------------------------------


def update_static_nodes(dag, nodes, funcs, col):
    with col:
        for node in [node for node in nodes if node not in dag.roots]:
            kwargs = dict()
            for arg in list(funcs[node].sig.names):
                arg_type = str(funcs[node].sig.annotations[arg])
                if "typing.Iterable" in arg_type:
                    kwargs[arg] = [int(num) for num in st.session_state[arg].split(",")]
                elif "typing.Mapping" in arg_type:
                    kwargs[arg] = dict(
                        tp=st.session_state[f"{arg}_tp"],
                        fn=st.session_state[f"{arg}_fn"],
                        fp=st.session_state[f"{arg}_fp"],
                        tn=st.session_state[f"{arg}_tn"],
                    )
                else:
                    kwargs[arg] = st.session_state[arg]
            val = funcs[node].func(**kwargs)
            if isinstance(val, dict):
                for key in val.keys():
                    st.session_state[f"{node}_{key}"] = val[key]
                with st.beta_expander(node):
                    for key in val.keys():
                        st.write(f"{key}: {st.session_state[f'{node}_{key}']}")
            else:
                st.session_state[node] = funcs[node].func(**kwargs)
                st.write(f"{node}: {st.session_state[node]}")


def binary_classification_factory(dag, nodes, funcs, values, arg_types, col):
    with col:
        for node in dag.sig.names:
            st_kwargs = dict(
                value=values[node],
                on_change=update_static_nodes,
                args=(dag, nodes, funcs, col),
                key=node,
            )
            if arg_types[node] == "dict":
                with ARG_WIDGET_MAP["dict"](node):
                    for condition in values[node].keys():
                        st_kwargs["value"] = values[node][condition]
                        st_kwargs["key"] = f"{node}_{condition}"
                        st.number_input(condition, **st_kwargs)
            else:
                widget = ARG_WIDGET_MAP[arg_types[node]]
                widget(node, **st_kwargs)


# ------------------------------------ STANDARD UTILS ------------------------------------


def display_factory(dag, nodes, funcs, values, slider, ranges, col):
    with col:
        for node in nodes:
            st_kwargs = dict(
                value=values[node],
                on_change=update_nodes,
                args=(dag, funcs),
                key=node,
            )
            if slider:
                st_kwargs["min_value"] = ranges[node][0]
                st_kwargs["max_value"] = ranges[node][1]
                st.slider(node, *st_kwargs)
            else:
                st.number_input(node, **st_kwargs)


def update_nodes(dag, funcs):
    for node in dag.var_nodes:
        if node not in dag.roots:
            args = [st.session_state[arg] for arg in list(funcs[node].src_names.keys())]
            st.session_state[node] = funcs[node].func(*args)


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
            st_error(
                "You need to define if you want slider or number input in your configs!"
            )
        elif config["slider"]:
            if "ranges" not in config:
                st_error("You need to define your slider ranges if you want sliders!")
            else:
                if not isinstance(config["ranges"], dict):
                    st_error(
                        "You need to define your slider ranges as a dictionary of two-element lists!"
                    )
                elif not set(get_nodes(dag)).issubset(set(config["ranges"].keys())):
                    st_error(
                        "You need to define a slider range for every component of your DAG!"
                    )


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
