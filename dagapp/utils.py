"""Utils"""

import numpy as np
import pandas as pd
import streamlit as st
from typing import Mapping, Iterable
from meshed.itools import successors
from lined import iterize

DFLT_VALS = {
    int: 0,
    float: 0.0,
    Iterable[int]: '0,0,0,0',
    Mapping[str, int]: dict(tp=0, fn=0, fp=0, tn=0),
    bool: False,
}

DFLT_ANNOT_ARGTYPE_MAP = {
    int: 'num',
    float: 'num',
    str: 'text',
    bool: 'bool',
    list: 'list',
    dict: 'dict',
}

ARG_TYPE_WIDGET_MAP = {
    'num': st.number_input,
    'slider': st.slider,
    'double_slider': st.expander,
    'text': st.text_input,
    'list': st.text_input,
    'dict': st.expander,
}


# ------------------------------------ VECTORIZATION  ------------------------------------


def get_vec_input(node):
    """
    Returns a vectorized input defined by a double slider
    """
    return np.linspace(
        start=int(st.session_state[f'{node}_values'][0]),
        stop=int(st.session_state[f'{node}_values'][1]),
        num=int(st.session_state[f'{node}_num']),
        endpoint=True,
    )


def get_args(dag, node, funcs):
    """
    Returns the arguments for a vectorized FuncNode
    """
    args = list()
    for arg in list(funcs[node].sig.names):
        if arg in dag.roots:
            vec_input = get_vec_input(arg)
            if arg in funcs[node].sig.annotations:
                arg_type = str(funcs[node].sig.annotations[arg])
                if arg_type == 'int':
                    args.append(list(vec_input.astype(int)))
                else:
                    args.append(list(vec_input))
            else:
                args.append(list(vec_input))
        else:
            args.append(st.session_state[arg])
    return args


def display_vec_node(node, funcs, args):
    """
    Displays a non-root-node for vectorized input
    """
    func = iterize(funcs[node].func)
    val = list(func(*args))
    st.session_state[node] = val
    st.write(f'{node}: ')
    st.write(pd.DataFrame(st.session_state[node]))


def mk_double_slider(node, st_kwargs, col):
    """
    Create a double slider for a given node
    """
    with col:
        with st.expander(node):
            st.slider(
                'vectorization range',
                min_value=0,
                max_value=100,
                value=(10, 90),
                key=f'{node}_values',
                **st_kwargs,
            )
            st.number_input(
                'num values', min_value=1, value=5, key=f'{node}_num', **st_kwargs
            )
            st.write(pd.DataFrame(get_vec_input(node)).transpose())


def vector_factory(dag, nodes, funcs, col):
    """
    Displays the root nodes of a vectorized DAG as double sliders
    """
    with col:
        for node in dag.sig.names:
            st_kwargs = dict(on_change=update_vec_nodes, args=(dag, nodes, funcs, col),)
            mk_double_slider(node, st_kwargs, col)


def update_vec_nodes(dag, nodes, funcs, col):
    """
    Update non root-nodes for vectorized DAG factory
    """
    with col:
        for node in [node for node in nodes if node not in dag.roots]:
            args = get_args(dag, node, funcs)
            if len(set(map(len, [arg for arg in args]))) == 1:
                display_vec_node(node, funcs, args)
            else:
                break


# ------------------------------------ STATIC NODES ------------------------------------


def get_kwargs(node, funcs):
    """
    Get keyword arguments for a FuncNode
    """
    kwargs = dict()
    for arg in list(funcs[node].sig.names):
        if arg in funcs[node].sig.annotations:
            arg_type = str(funcs[node].sig.annotations[arg])
        else:
            arg_type = str(float)
        if 'typing.Iterable' in arg_type:
            kwargs[arg] = [int(num) for num in st.session_state[arg].split(',')]
        elif 'typing.Mapping' in arg_type:
            kwargs[arg] = dict(
                tp=st.session_state[f'{arg}_tp'],
                fn=st.session_state[f'{arg}_fn'],
                fp=st.session_state[f'{arg}_fp'],
                tn=st.session_state[f'{arg}_tn'],
            )
        else:
            kwargs[arg] = st.session_state[arg]
    return kwargs


def update_static_nodes(dag, nodes, funcs, col):
    """
    Updates the non-root nodes for a static DAG factory
    """
    with col:
        for node in [node for node in nodes if node not in dag.roots]:
            kwargs = get_kwargs(node, funcs)
            val = funcs[node].func(**kwargs)
            if isinstance(val, dict):
                for key in val.keys():
                    st.session_state[f'{node}_{key}'] = val[key]
                with st.expander(node):
                    for key in val.keys():
                        st.write(f"{key}: {st.session_state[f'{node}_{key}']}")
            else:
                st.session_state[node] = val
                st.write(f'{node}: {st.session_state[node]}')


def static_factory(dag, nodes, funcs, values, arg_types, ranges, col):
    """
    Displays the root nodes of a dag
    """
    with col:
        for node in dag.sig.names:
            st_kwargs = dict(
                value=values[node],
                on_change=update_static_nodes,
                args=(dag, nodes, funcs, col),
                key=node,
            )
            display_node(node, arg_types, ranges, values, st_kwargs)


# ------------------------------------ INTERMEDIATE NODES ------------------------------------


def display_node(node, arg_types, ranges, values, st_kwargs):
    """
    Displays the given node based on the argument type
    """
    if node in arg_types:
        if arg_types[node] == 'dict':
            with ARG_TYPE_WIDGET_MAP['dict'](node):
                for condition in values[node].keys():
                    st_kwargs['value'] = values[node][condition]
                    st_kwargs['key'] = f'{node}_{condition}'
                    st.number_input(condition, **st_kwargs)
        elif arg_types[node] == 'slider':
            st_kwargs['min_value'] = ranges[node][0]
            st_kwargs['max_value'] = ranges[node][1]
            st.slider(node, **st_kwargs)
        elif arg_types[node] == 'bool':
            # streamlit.radio does not accept a 'value' kwarg; use checkbox
            # for boolean inputs which supports 'value' and the same
            # on_change/key/args parameters.
            st.checkbox(
                node,
                value=values[node],
                key=st_kwargs.get('key'),
                on_change=st_kwargs.get('on_change'),
                args=st_kwargs.get('args'),
            )
        else:
            widget = ARG_TYPE_WIDGET_MAP[arg_types[node]]
            widget(node, **st_kwargs)
    else:
        st.number_input(node, **st_kwargs)


def display_factory(dag, nodes, funcs, values, arg_types, ranges, col):
    """
    Display the nodes of a dag with number of slider inputs
    """
    with col:
        for node in nodes:
            st_kwargs = dict(
                value=values[node],
                on_change=update_nodes,
                args=(dag, node, funcs),
                key=node,
            )
            display_node(node, arg_types, ranges, values, st_kwargs)
        st.button(
            'Reload DAG from root nodes', on_click=reload_nodes, args=(dag, funcs)
        )


def reload_nodes(dag, funcs):
    """
    Updates all nodes based on the values of the root nodes
    """
    for node in dag.var_nodes:
        if node not in dag.roots:
            args = [st.session_state[arg] for arg in list(funcs[node].sig.names)]
            st.session_state[node] = funcs[node].func(*args)


def update_nodes(dag, node_ch, funcs):
    """
    Updates successors of a changed node
    """
    sub_nodes = [
        node for node in list(successors(dag.graph, node_ch)) if isinstance(node, str)
    ]
    for node in sub_nodes:
        args = [st.session_state[arg] for arg in list(funcs[node].sig.names)]
        st.session_state[node] = funcs[node].func(*args)


# ------------------------------------ STANDARD UTILS ------------------------------------


def get_root_values(dag):
    """
    Returns the default values for all the root nodes found in dag
    """
    root_defaults = dict()
    for name in dag.sig.names:
        if name in dag.sig.defaults:
            dflt = dag.sig.defaults[name]
            if dflt is not None:
                root_defaults[name] = dflt
        elif name in dag.sig.annotations:
            root_defaults[name] = DFLT_VALS[dag.sig.annotations[name]]
        else:
            root_defaults[name] = 0.0
    return root_defaults


def get_func_values(defaults, funcs):
    """
    Returns the default values for all the FuncNodes in funcs using the root defaults in defaults
    """
    func_defaults = defaults
    for name in funcs:
        func_node = funcs[name]
        if set(func_node.sig.names).issubset(set(list(func_defaults.keys()))):
            kwargs = dict()
            for arg_name in func_node.sig.names:
                kwargs[arg_name] = func_defaults[arg_name]
            func_defaults[name] = func_node.func(**kwargs)
    return func_defaults


def get_values(dag, funcs):
    """
    Returns default values for all the nodes found in dag
    """
    root_defaults = get_root_values(dag)
    func_defaults = get_func_values(root_defaults, funcs)
    return func_defaults


def get_nodes(dag):
    """
    Returns the names of all nodes found in dag
    """
    nodes = dag.sig.names
    for node in dag.nodes:
        if node not in nodes and isinstance(node, str):
            nodes.append(node)
    return nodes


def get_funcs(dag):
    """
    Returns the names of all the FuncNodes found in dag
    """
    funcs = dict()
    for func_node in dag.func_nodes:
        funcs[func_node.name[:-1]] = func_node
    return funcs


def get_from_configs(configs):
    """
    Obtains information from user defined configs
    """
    arg_types = configs['arg_types']
    ranges = None if 'ranges' not in configs else configs['ranges']
    return arg_types, ranges


def get_default_configs(dags):
    """
    Returns default configs based on dags if the user did not provide them
    """
    configs = []
    for dag in dags:
        config = {'arg_types': {}}
        for node in dag.roots:
            if node in dag.sig.annotations:
                config['arg_types'][node] = DFLT_ANNOT_ARGTYPE_MAP[
                    dag.sig.annotations[node]
                ]
            else:
                config['arg_types'][node] = 'num'
        configs.append(config)
    return configs


def check_configs(dags, configs):
    """
    Checks the user defined configs to prevent errors
    """
    if len(configs) != len(dags):
        st_error('You need to define configs for all of your DAGs!')
    for dag, config in zip(dags, configs):
        # config should be a dict containing an 'arg_types' mapping
        if not isinstance(config, dict):
            st_error(
                'Each config must be a dict containing "arg_types" and optional "ranges".'
            )

        if 'arg_types' not in config:
            st_error('You need to define an argument type for your root nodes!')
        else:
            # ensure arg_types provides an entry per root node
            if len(config['arg_types']) < len(dag.roots):
                st_error(
                    'You need to define an argument type for all of your root nodes!'
                )

            # if any of the arg types is a slider, ensure ranges are provided
            if 'slider' in config['arg_types'].values():
                if 'ranges' not in config:
                    st_error(
                        'You need to define slider ranges if you want to set slider as an argument type!'
                    )


def st_error(message):
    """
    Raises a streamlit error with the given message
    """
    st.error(message)
    st.stop()
