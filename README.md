# dagapp
Making apps from DAGs by just snapping your fingers

To install:	```pip install dagapp```

[What's a DAG?](https://en.wikipedia.org/wiki/Directed_acyclic_graph)

[What's an app?](https://www.amazon.com/Life-Real-Dummies-Clueless-1996-10-03/dp/B01F81N4D0)

This is a beautiful example of a DAG app woven into to an article: [rent-or-buy article+app](https://www.nytimes.com/interactive/2024/upshot/buy-rent-calculator.html)
The app serves as an illustration of the article and the article as the documentation of the app. (Note: It was a lot more "beautiful" in 2014, but they changed the graphic now! Boo!)

Here's [another example of interactive calculators](https://www.mottomortgage.com/offices/makers-chattanooga/mortgage-calculators). 

What `dagapp` wants to become is a framework to generate such effective communication, effortlessly. 

Enough theory. Here's how it works...


### A simple example

#### First make a DAG

```python
from meshed.dag import DAG

def b(a):
    return 2 ** a


def d(c):
    return 10 - (5 ** c)


def result(b, d):
    return b * d
    
dag = DAG((b, d, result))
```

#### Then make an app

```python
from dagapp.base import dag_app
from functools import partial

dags = [dag]

if __name__ == "__main__":
    app = partial(dag_app, dags=dags)
    app()
```

#### Then run the app

```
>>> streamlit run example.py
```

#### ... and this is what you get

![png](https://github.com/i2mint/dagapp/blob/master/docs/images/simple_example.png?raw=true)


### A more complicated example

Let's say we want to create two different DAGs and view them on the same streamlit page, keep all the non-root nodes static and represent the number inputs for one of the DAGs as sliders. We will use functions defined in `configs_example.py` for this example.

#### Define the DAGs

To start we can create our DAGs just like in the previous example.
```python
profit_dag = DAG((user_clicks, rev, cost, profit))
revenue_dag = DAG((partners, clicks, revenue))

dags = [profit_dag, revnue_dag]
```

#### Define the configs

Next we can define some configs for these DAGs. These configs should be a list of dictionaries, with each dictionary representing the configs for each DAG. Each config must contain a dictionary `arg_types` that matches each of the root nodes in the DAG to an input type (currently the options are: num, slider, text, list, dict). If `arg_types` is not explicitly defined, then it will try to infer from type annotations in the function definitions, and then default to num. If slider is defined as the `arg_type` for any of the root nodes, then another dictionary `ranges` must be defined that matches each of the nodes designated to be slider with a min and max value for that slider. The configs for this example can be seen below.
```python
configs = [
    dict(
        arg_types=dict(
            a="num",
            b="num",
            cost_per_click="num",
            revenue_per_click="num",
        ),
    ),
    dict(
        arg_types=dict(
            max_partners="slider",
            cost_per_click="slider",
            price_elasticity="slider",
            partners="slider",
            clicks_per_partner="slider",
        ),
        ranges=dict(
            max_partners=[0, 2000],
            cost_per_click=[0.0, 1.0],
            price_elasticity=[0, 200],
            partners=[0, 1500],
            clicks_per_partner=[0.0, 10.0],
        ),
    ),
]
```

#### Make the app

We can now make our app in a similar manner as the previous example, this time defining our configs, as well as defining `StaticPageFunc` as our page factory to keep all non-root nodes static.
```
from dagapp.page_funcs import StaticPageFunc

if __name__ == "__main__":
    app = partial(dag_app, dags=dags, page_factory=StaticPageFunc, configs=configs)
    app()
```

#### Run the app

```
>>> streamlit run configs_example.py
```

#### ... and this is what you get

![png](https://github.com/i2mint/dagapp/blob/master/docs/images/configs_example_1.png?raw=true)
![png](https://github.com/i2mint/dagapp/blob/master/docs/images/configs_example_2.png?raw=true)
