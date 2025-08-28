"""
Rent or Buy.

Based on this article:
"""

import math


def calculate_rent_vs_buy(
    years_to_evaluate=30,
    # Default values extracted from the original NYT article's JavaScript
    home_price=500000,
    down_payment_percent=0.20,
    mortgage_interest_rate=0.07,
    property_tax_rate=0.01,
    home_insurance_annual=1500,
    maintenance_percent=0.01,
    closing_cost_percent=0.02,
    selling_cost_percent=0.06,
    annual_rent=24000,
    rent_increase_rate=0.03,
    home_value_growth_rate=0.04,
    investment_return_rate=0.06,
    marginal_tax_rate=0.25,
    loan_term_years=30,
    inflation_rate=0.025,
):
    """
    Calculates and compares the total net present value of buying vs. renting a home
    over a specified number of years, based on the logic from the NYT calculator.

    Args:
        years_to_evaluate (int): The number of years to run the simulation.
        ... (other arguments for financial variables with default values)

    Returns:
        A dictionary containing the total accumulated costs for both scenarios and
        the breakeven year.
    """

    # Initialize variables for both scenarios
    npv_buy_total = 0.0
    npv_rent_total = 0.0
    breakeven_year = None

    # Initial setup for buying scenario
    principal = home_price * (1 - down_payment_percent)
    closing_costs = home_price * closing_cost_percent

    # Amortization formula to calculate monthly mortgage payment
    monthly_interest_rate = mortgage_interest_rate / 12
    num_payments = loan_term_years * 12

    if monthly_interest_rate > 0:
        monthly_mortgage_payment = principal * (
            monthly_interest_rate
            / (1 - math.pow(1 + monthly_interest_rate, -num_payments))
        )
    else:
        # Handle case where interest rate is 0
        monthly_mortgage_payment = principal / num_payments

    current_loan_balance = principal
    total_interest_paid_yearly = 0.0

    # Initial investment for renting scenario (down payment + closing costs)
    initial_rent_investment = (home_price * down_payment_percent) + closing_costs
    rent_investment_value = initial_rent_investment

    # Main simulation loop
    for year in range(1, years_to_evaluate + 1):

        # --- BUYING SCENARIO CALCULATIONS ---

        # Calculate yearly costs
        annual_property_tax = home_price * property_tax_rate
        annual_maintenance = home_price * maintenance_percent
        annual_insurance = home_insurance_annual

        # Calculate mortgage interest paid for the year and update loan balance
        annual_principal_paid = 0.0
        total_interest_paid_yearly = 0.0

        if year <= loan_term_years:
            for _ in range(12):
                interest_this_month = current_loan_balance * monthly_interest_rate
                principal_this_month = monthly_mortgage_payment - interest_this_month
                current_loan_balance -= principal_this_month
                total_interest_paid_yearly += interest_this_month
                annual_principal_paid += principal_this_month

        # Calculate tax deductions on mortgage interest and property taxes
        tax_deduction = (
            total_interest_paid_yearly + annual_property_tax
        ) * marginal_tax_rate

        # Total annual cost of buying before selling and home appreciation
        buy_cost_this_year = (
            (monthly_mortgage_payment * 12)
            + annual_property_tax
            + annual_maintenance
            + annual_insurance
            - tax_deduction
        )

        # Update home value for the year
        home_value_after_year = home_price * math.pow(1 + home_value_growth_rate, year)

        # Calculate selling cost and equity at the end of the simulation
        if year == years_to_evaluate:
            selling_cost = home_value_after_year * selling_cost_percent

            # Calculate total equity gained from principal payments and appreciation
            total_equity = home_value_after_year - current_loan_balance

            # Final costs and gains
            buy_cost_this_year += selling_cost
            buy_cost_this_year -= total_equity

        # Discount annual cost back to present value
        npv_buy_total += buy_cost_this_year / math.pow(1 + inflation_rate, year)

        # --- RENTING SCENARIO CALCULATIONS ---

        # Annual cost of rent
        annual_rent_cost = annual_rent * math.pow(1 + rent_increase_rate, year - 1)

        # Calculate additional funds invested from not buying
        rent_savings_invested = (
            (monthly_mortgage_payment * 12)
            + (home_price * property_tax_rate)
            + (home_price * maintenance_percent)
            + home_insurance_annual
        )

        # The key difference from the original NYT logic is that the invested rent savings
        # are calculated separately and compounded. The provided HTML logic does this
        # on an NPV basis. Let's stick to the NPV model for direct comparison.

        # Discount annual rent cost back to present value
        npv_rent_total += annual_rent_cost / math.pow(1 + inflation_rate, year)

        # Account for investment gains
        # The original script's logic for NPV of investments is complex.
        # This simplified version adds the gains from the initial investment.
        rent_investment_value = rent_investment_value * (1 + investment_return_rate)

        # Update breakeven year
        if breakeven_year is None and npv_buy_total < npv_rent_total:
            breakeven_year = year

    # The original script adds the down payment and closing costs to the final NPV
    # This is a common practice to include initial costs in the total NPV calculation
    npv_buy_total += home_price * down_payment_percent + closing_costs
    npv_rent_total -= rent_investment_value

    return {
        'npv_buy_total': int(npv_buy_total),  # rounding to the nearest int
        'npv_rent_total': int(npv_rent_total),  # rounding to the nearest int
        'breakeven_year': breakeven_year,
    }


if __name__ == '__main__':

    from dagapp.base import dag_app

    from meshed.dag import DAG
    from functools import partial

    rendering_kind = 'static_page_func'

    if rendering_kind == 'static_page_func':
        from dagapp.page_funcs import StaticPageFunc

        app = partial(
            dag_app, dags=[DAG((calculate_rent_vs_buy,))], page_factory=StaticPageFunc
        )
    elif rendering_kind == 'json_page_func' or rendering_kind == 'table_page_func':
        # Custom page function that renders dict outputs as JSON or as a one-row table
        import pandas as pd
        import streamlit as st

        from dagapp.page_funcs import BasePageFunc
        from dagapp.utils import (
            get_funcs,
            get_nodes,
            get_values,
            get_from_configs,
            display_node,
            get_kwargs,
        )

        def format_display_value(v):
            """Format numeric values for display: no decimals and space as thousands separator.

            - ints -> "123 456"
            - floats -> rounded to nearest int and formatted as above
            - iterables -> format each element
            - other types returned unchanged
            """
            # handle numpy scalars/arrays
            try:
                import numpy as _np
            except Exception:
                _np = None

            def fmt_num(x):
                try:
                    if _np is not None and isinstance(x, _np.generic):
                        x = x.item()
                    if isinstance(x, bool):
                        return x
                    if isinstance(x, int):
                        return f'{x:,}'.replace(',', ' ')
                    if isinstance(x, float):
                        # round to nearest integer for display
                        return f'{int(round(x)):,}'.replace(',', ' ')
                except Exception:
                    pass
                return x

            # lists/tuples/ndarrays
            if (
                _np is not None
                and hasattr(_np, 'ndarray')
                and isinstance(v, _np.ndarray)
            ):
                return [fmt_num(x) for x in v.tolist()]
            if isinstance(v, (list, tuple)):
                return [fmt_num(x) for x in v]

            if isinstance(v, dict):
                # format dict values recursively
                return {k: format_display_value(val) for k, val in v.items()}

            return fmt_num(v)

        def update_static_nodes_dict(dag, nodes, funcs, col):
            """Update non-root nodes and render dict outputs as JSON/table."""
            with col:
                for node in [node for node in nodes if node not in dag.roots]:
                    kwargs = get_kwargs(node, funcs)
                    val = funcs[node].func(**kwargs)
                    if isinstance(val, dict):
                        # format values for display
                        disp_val = format_display_value(val)
                        with st.expander(node):
                            if rendering_kind == 'json_page_func':
                                st.json(disp_val)
                            else:
                                # table: render dict as a single-row DataFrame
                                st.table(pd.DataFrame([disp_val]))
                    else:
                        st.session_state[node] = val
                        st.write(f'{node}: {st.session_state[node]}')

        def reload_nodes_dict(dag, funcs):
            for node in dag.var_nodes:
                if node not in dag.roots:
                    args = [
                        st.session_state[arg] for arg in list(funcs[node].sig.names)
                    ]
                    st.session_state[node] = funcs[node].func(*args)

        class DictPageFunc(BasePageFunc):
            def __call__(self):
                if self.page_title:
                    st.markdown(f'''## **{self.page_title}**''')

                c1, c2 = st.columns(2)

                c2.graphviz_chart(self.dag.dot_digraph())
                funcs = get_funcs(self.dag)
                nodes = get_nodes(self.dag)
                values = get_values(self.dag, funcs)
                arg_types, ranges = get_from_configs(self.configs)

                with c1:
                    for node in self.dag.sig.names:
                        st_kwargs = dict(
                            value=values[node],
                            on_change=update_static_nodes_dict,
                            args=(self.dag, nodes, funcs, c1),
                            key=node,
                        )
                        display_node(node, arg_types, ranges, values, st_kwargs)

                    st.button(
                        'Reload DAG from root nodes',
                        on_click=reload_nodes_dict,
                        args=(self.dag, funcs),
                    )

                # initial render
                update_static_nodes_dict(self.dag, nodes, funcs, c1)

        app = partial(
            dag_app, dags=[DAG((calculate_rent_vs_buy,))], page_factory=DictPageFunc
        )
    else:
        raise ValueError(f'Unknown rendering kind: {rendering_kind}')

    app()
