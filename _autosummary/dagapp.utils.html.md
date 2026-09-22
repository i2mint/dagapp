# dagapp.utils

Utils

### Functions

| [`check_configs`](#dagapp.utils.check_configs)(dags, configs)                    | Checks the user defined configs to prevent errors                                             |
|--------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| [`display_factory`](#dagapp.utils.display_factory)(dag, nodes, funcs, values, ...) | Display the nodes of a dag with number of slider inputs                                       |
| [`display_node`](#dagapp.utils.display_node)(node, arg_types, ranges, ...)      | Displays the given node based on the argument type                                            |
| [`display_vec_node`](#dagapp.utils.display_vec_node)(node, funcs, args)             | Displays a non-root-node for vectorized input                                                 |
| [`get_args`](#dagapp.utils.get_args)(dag, node, funcs)                      | Returns the arguments for a vectorized FuncNode                                               |
| [`get_default_configs`](#dagapp.utils.get_default_configs)(dags)                       | Returns default configs based on dags if the user did not provide them                        |
| [`get_from_configs`](#dagapp.utils.get_from_configs)(configs)                       | Obtains information from user defined configs                                                 |
| [`get_func_values`](#dagapp.utils.get_func_values)(defaults, funcs)                | Returns the default values for all the FuncNodes in funcs using the root defaults in defaults |
| [`get_funcs`](#dagapp.utils.get_funcs)(dag)                                  | Returns the names of all the FuncNodes found in dag                                           |
| [`get_kwargs`](#dagapp.utils.get_kwargs)(node, funcs)                         | Get keyword arguments for a FuncNode                                                          |
| [`get_nodes`](#dagapp.utils.get_nodes)(dag)                                  | Returns the names of all nodes found in dag                                                   |
| [`get_root_values`](#dagapp.utils.get_root_values)(dag)                            | Returns the default values for all the root nodes found in dag                                |
| [`get_values`](#dagapp.utils.get_values)(dag, funcs)                          | Returns default values for all the nodes found in dag                                         |
| [`get_vec_input`](#dagapp.utils.get_vec_input)(node)                             | Returns a vectorized input defined by a double slider                                         |
| [`mk_double_slider`](#dagapp.utils.mk_double_slider)(node, st_kwargs, col)          | Create a double slider for a given node                                                       |
| [`reload_nodes`](#dagapp.utils.reload_nodes)(dag, funcs)                        | Updates all nodes based on the values of the root nodes                                       |
| [`st_error`](#dagapp.utils.st_error)(message)                               | Raises a streamlit error with the given message                                               |
| [`static_factory`](#dagapp.utils.static_factory)(dag, nodes, funcs, values, ...)  | Displays the root nodes of a dag                                                              |
| [`update_nodes`](#dagapp.utils.update_nodes)(dag, node_ch, funcs)               | Updates successors of a changed node                                                          |
| [`update_static_nodes`](#dagapp.utils.update_static_nodes)(dag, nodes, funcs, col)     | Updates the non-root nodes for a static DAG factory                                           |
| [`update_vec_nodes`](#dagapp.utils.update_vec_nodes)(dag, nodes, funcs, col)        | Update non root-nodes for vectorized DAG factory                                              |
| [`vector_factory`](#dagapp.utils.vector_factory)(dag, nodes, funcs, col)          | Displays the root nodes of a vectorized DAG as double sliders                                 |

### dagapp.utils.check_configs(dags, configs)

Checks the user defined configs to prevent errors

### dagapp.utils.display_factory(dag, nodes, funcs, values, arg_types, ranges, col)

Display the nodes of a dag with number of slider inputs

### dagapp.utils.display_node(node, arg_types, ranges, values, st_kwargs)

Displays the given node based on the argument type

### dagapp.utils.display_vec_node(node, funcs, args)

Displays a non-root-node for vectorized input

### dagapp.utils.get_args(dag, node, funcs)

Returns the arguments for a vectorized FuncNode

### dagapp.utils.get_default_configs(dags)

Returns default configs based on dags if the user did not provide them

### dagapp.utils.get_from_configs(configs)

Obtains information from user defined configs

### dagapp.utils.get_func_values(defaults, funcs)

Returns the default values for all the FuncNodes in funcs using the root defaults in defaults

### dagapp.utils.get_funcs(dag)

Returns the names of all the FuncNodes found in dag

### dagapp.utils.get_kwargs(node, funcs)

Get keyword arguments for a FuncNode

### dagapp.utils.get_nodes(dag)

Returns the names of all nodes found in dag

### dagapp.utils.get_root_values(dag)

Returns the default values for all the root nodes found in dag

### dagapp.utils.get_values(dag, funcs)

Returns default values for all the nodes found in dag

### dagapp.utils.get_vec_input(node)

Returns a vectorized input defined by a double slider

### dagapp.utils.mk_double_slider(node, st_kwargs, col)

Create a double slider for a given node

### dagapp.utils.reload_nodes(dag, funcs)

Updates all nodes based on the values of the root nodes

### dagapp.utils.st_error(message)

Raises a streamlit error with the given message

### dagapp.utils.static_factory(dag, nodes, funcs, values, arg_types, ranges, col)

Displays the root nodes of a dag

### dagapp.utils.update_nodes(dag, node_ch, funcs)

Updates successors of a changed node

### dagapp.utils.update_static_nodes(dag, nodes, funcs, col)

Updates the non-root nodes for a static DAG factory

### dagapp.utils.update_vec_nodes(dag, nodes, funcs, col)

Update non root-nodes for vectorized DAG factory

### dagapp.utils.vector_factory(dag, nodes, funcs, col)

Displays the root nodes of a vectorized DAG as double sliders
