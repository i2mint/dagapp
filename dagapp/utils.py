"""Utils"""

import streamlit as st
from typing import Mapping, Iterable

DFLT_VALS = {
    int: 0,
    float: 0.0,
    Iterable[int]: "0,0,0,0",
    Mapping[str, int]: dict(tp=0, fn=0, fp=0, tn=0),
}

DFLT_ANNOT_ARGTYPE_MAP = {
    int: "num",
    float: "num",
    str: "text",
    list: "list",
    dict: "dict",
}

ARG_WIDGET_MAP = {
    "num": st.number_input,
    "slider": st.slider,
    "text": st.text_input,
    "list": st.text_input,
    "dict": st.beta_expander,
}


# ------------------------------------ BINARY CLASSIFICATION ------------------------------------


def update_static_nodes(dag, nodes, funcs, col):
    with col:
        for node in [node for node in nodes if node not in dag.roots]:
            kwargs = dict()
            for arg in list(funcs[node].sig.names):
                if arg in funcs[node].sig.annotations:
                    arg_type = str(funcs[node].sig.annotations[arg])
                else:
                    arg_type = str(float)
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


def static_factory(dag, nodes, funcs, values, arg_types, ranges, col):
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
            elif arg_types[node] == "slider":
                st_kwargs["min_value"] = ranges[node][0]
                st_kwargs["max_value"] = ranges[node][1]
                st.slider(node, **st_kwargs)
            else:
                widget = ARG_WIDGET_MAP[arg_types[node]]
                widget(node, **st_kwargs)


# ------------------------------------ STANDARD UTILS ------------------------------------


def get_from_configs(configs):
    arg_types = configs["arg_types"]
    ranges = None if "ranges" not in configs else configs["ranges"]
    return arg_types, ranges


def display_factory(dag, nodes, funcs, values, arg_types, ranges, col):
    with col:
        for node in nodes:
            st_kwargs = dict(
                value=values[node],
                on_change=update_nodes,
                args=(dag, funcs),
                key=node,
            )
            if node in arg_types:
                if arg_types[node] == "slider":
                    st_kwargs["min_value"] = ranges[node][0]
                    st_kwargs["max_value"] = ranges[node][1]
                    st.slider(node, *st_kwargs)
                else:
                    st.number_input(node, **st_kwargs)
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


def get_default_configs(dags):
    configs = []
    for dag in dags:
        config = {"arg_types": {}}
        for node in dag.roots:
            if node in dag.sig.annotations:
                config["arg_types"][node] = DFLT_ANNOT_ARGTYPE_MAP[
                    dag.sig.annotations[node]
                ]
            else:
                config["arg_types"][node] = "num"
        configs.append(config)
    return configs


def check_configs(dags, configs):
    if len(configs) != len(dags):
        st_error("You need to define configs for all of your DAGs!")

    for dag, config in zip(dags, configs):
        if "arg_types" not in config:
            st_error("You need to define an argument type for your root nodes!")
        else:
            if len("arg_types") < len(dag.roots):
                st_error(
                    "You need to define an argument type for all of your root nodes!"
                )

            if "slider" in config["arg_types"]:
                if "ranges" not in config:
                    st_error(
                        "You need to define slider ranges if you want to set slider as an argument type!"
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
