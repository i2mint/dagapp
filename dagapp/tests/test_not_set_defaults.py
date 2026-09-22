"""``i2``'s ``NotSet`` sentinel in a signature means "required / no default".

See i2mint/i2#48: once ``i2.FuncFactory`` shows ``NotSet`` defaults, a DAG root with
such a default must get the same initial value as one with no default at all.
These tests use ``i2.deco.NotSet`` directly, so they pass with any i2 version.
"""

from i2.deco import NotSet
from meshed import DAG

from dagapp.utils import get_root_values


def f(a: int, b, c: float = 2.0):
    return a + b + c


# ``f`` with ``NotSet`` defaults, as a re-landed i2#88 ``FuncFactory`` would show.
def f_with_not_set(a: int = NotSet, b=NotSet, c: float = 2.0):
    return a + b + c


f_with_not_set.__name__ = f.__name__


def test_root_values_ignore_not_set():
    got = get_root_values(DAG([f_with_not_set]))
    assert NotSet not in got.values()
    assert got == get_root_values(DAG([f]))
