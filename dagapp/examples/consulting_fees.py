"""Compute consulting fees

All common parameter defaults are centralized in the `dflt` single-source-of-truth
so functions that share parameter names also share the same defaults. This
avoids signature conflicts when building a DAG using meshed (parameter merging).
"""

from typing import Literal
from types import SimpleNamespace

from dagapp.base import dag_app
from meshed.dag import DAG
from functools import partial

# Single source of truth for shared defaults used across function signatures.
# Use attribute access (dflt.<name>) so defaults are clearly named and grouped.
dflt = SimpleNamespace(
    # billing defaults
    retainer=True,
    ad_hoc_day_rate=2800.0,
    retainer_day_rate=2400.0,
    # time defaults
    hours_per_day=8.0,
    committed_days=8.0,
    ramp_up_days=0.0,
    # percentage / rates
    flex_premium_pct=0.10,
    vat_rate=0.081,
)


def effective_day_rate(
    retainer: bool = dflt.retainer,
    ad_hoc_day_rate: float = dflt.ad_hoc_day_rate,
    retainer_day_rate: float = dflt.retainer_day_rate,
) -> float:
    """Return the effective day-rate based on retainer flag."""
    return retainer_day_rate if retainer else ad_hoc_day_rate


def effective_hourly_rate(
    effective_day_rate: float, hours_per_day: float = dflt.hours_per_day,
) -> float:
    """Return the hourly equivalent of the effective day-rate."""
    return effective_day_rate / hours_per_day


def committed_days(tier: Literal['light', 'regular', 'deep'] = 'regular',) -> float:
    """Return default committed days/month for a named tier."""
    mapping = {'light': 4.0, 'regular': 8.0, 'deep': 12.0}
    return mapping[tier]


def base_fee_ex_vat(
    effective_day_rate: float, committed_days: float = dflt.committed_days,
) -> float:
    """Return the base monthly fee (ex-VAT) for committed days."""
    return effective_day_rate * committed_days


def flex_fee_ex_vat(
    effective_day_rate: float,
    ramp_up_days: float = dflt.ramp_up_days,
    flex_premium_pct: float = dflt.flex_premium_pct,
) -> float:
    """
    Return the flex (short-notice) component (ex-VAT).
    Applies only to additional ramp-up days beyond the commitment.
    """
    return effective_day_rate * ramp_up_days * flex_premium_pct


def subtotal_ex_vat(base_fee_ex_vat: float, flex_fee_ex_vat: float = 0.0,) -> float:
    """Return the subtotal (ex-VAT)."""
    return base_fee_ex_vat + flex_fee_ex_vat


def vat_amount(subtotal_ex_vat: float, vat_rate: float = dflt.vat_rate,) -> float:
    """Return the VAT amount."""
    return subtotal_ex_vat * vat_rate


def total_incl_vat(subtotal_ex_vat: float, vat_amount: float,) -> float:
    """Return the total including VAT."""
    return subtotal_ex_vat + vat_amount


# --- Convenience wrappers for common scenarios ---


def light_monthly_total_incl_vat(
    retainer: bool = dflt.retainer,
    ad_hoc_day_rate: float = dflt.ad_hoc_day_rate,
    retainer_day_rate: float = dflt.retainer_day_rate,
    ramp_up_days: float = dflt.ramp_up_days,
    flex_premium_pct: float = dflt.flex_premium_pct,
    vat_rate: float = dflt.vat_rate,
) -> float:
    """Return total incl. VAT for the 'light' (4 d/mo) scenario."""
    d = effective_day_rate(retainer, ad_hoc_day_rate, retainer_day_rate)
    base = base_fee_ex_vat(d, committed_days('light'))
    flex = flex_fee_ex_vat(d, ramp_up_days, flex_premium_pct)
    sub = subtotal_ex_vat(base, flex)
    vat = vat_amount(sub, vat_rate)
    return total_incl_vat(sub, vat)


def regular_monthly_total_incl_vat(
    retainer: bool = dflt.retainer,
    ad_hoc_day_rate: float = dflt.ad_hoc_day_rate,
    retainer_day_rate: float = dflt.retainer_day_rate,
    ramp_up_days: float = dflt.ramp_up_days,
    flex_premium_pct: float = dflt.flex_premium_pct,
    vat_rate: float = dflt.vat_rate,
) -> float:
    """Return total incl. VAT for the 'regular' (8 d/mo) scenario."""
    d = effective_day_rate(retainer, ad_hoc_day_rate, retainer_day_rate)
    base = base_fee_ex_vat(d, committed_days('regular'))
    flex = flex_fee_ex_vat(d, ramp_up_days, flex_premium_pct)
    sub = subtotal_ex_vat(base, flex)
    vat = vat_amount(sub, vat_rate)
    return total_incl_vat(sub, vat)


def deep_monthly_total_incl_vat(
    retainer: bool = dflt.retainer,
    ad_hoc_day_rate: float = dflt.ad_hoc_day_rate,
    retainer_day_rate: float = dflt.retainer_day_rate,
    ramp_up_days: float = dflt.ramp_up_days,
    flex_premium_pct: float = dflt.flex_premium_pct,
    vat_rate: float = dflt.vat_rate,
) -> float:
    """Return total incl. VAT for the 'deep' (12 d/mo) scenario."""
    d = effective_day_rate(retainer, ad_hoc_day_rate, retainer_day_rate)
    base = base_fee_ex_vat(d, committed_days('deep'))
    flex = flex_fee_ex_vat(d, ramp_up_days, flex_premium_pct)
    sub = subtotal_ex_vat(base, flex)
    vat = vat_amount(sub, vat_rate)
    return total_incl_vat(sub, vat)


# --- One-shot calculator when you just want the numbers quickly ---


def monthly_totals(
    committed_days: float = dflt.committed_days,
    ramp_up_days: float = dflt.ramp_up_days,
    retainer: bool = dflt.retainer,
    ad_hoc_day_rate: float = dflt.ad_hoc_day_rate,
    retainer_day_rate: float = dflt.retainer_day_rate,
    flex_premium_pct: float = dflt.flex_premium_pct,
    vat_rate: float = dflt.vat_rate,
) -> dict:
    """
    Return a dict with all intermediate values for transparency:
    effective_day_rate, base_fee_ex_vat, flex_fee_ex_vat, subtotal_ex_vat,
    vat_amount, total_incl_vat.
    """
    d = effective_day_rate(retainer, ad_hoc_day_rate, retainer_day_rate)
    base = base_fee_ex_vat(d, committed_days)
    flex = flex_fee_ex_vat(d, ramp_up_days, flex_premium_pct)
    sub = subtotal_ex_vat(base, flex)
    vat = vat_amount(sub, vat_rate)
    total = total_incl_vat(sub, vat)
    return {
        'effective_day_rate': d,
        'base_fee_ex_vat': base,
        'flex_fee_ex_vat': flex,
        'subtotal_ex_vat': sub,
        'vat_amount': vat,
        'total_incl_vat': total,
    }


def get_dag():
    funcs = {
        # "monthly_totals": monthly_totals,
        # "deep_monthly_total_incl_vat": deep_monthly_total_incl_vat,
        # "regular_monthly_total_incl_vat": regular_monthly_total_incl_vat,
        # "light_monthly_total_incl_vat": light_monthly_total_incl_vat,
        # "committed_days": committed_days,
        # "effective_hourly_rate": effective_hourly_rate,
        'effective_day_rate': effective_day_rate,
        'base_fee_ex_vat': base_fee_ex_vat,
        'flex_fee_ex_vat': flex_fee_ex_vat,
        'subtotal_ex_vat': subtotal_ex_vat,
        'vat_amount': vat_amount,
        'total_incl_vat': total_incl_vat,
    }

    dag = DAG(funcs.values())

    return dag


if __name__ == '__main__':
    dag = get_dag()
    collapsed_dag = DAG([dag], name='simple')
    dags = [collapsed_dag, dag]

    # configs = [
    #     {"page_name": "simple"},  # for collapsed_dag
    #     {"page_name": "details"},  # for dag
    # ]
    configs = None

    app = partial(dag_app, dags=dags, configs=configs)
    app()
