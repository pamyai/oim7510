#try1

import marimo

__generated_with = "0.24.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    import requests

    return duckdb, mo


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return (ask,)


@app.cell
def _():
    from datetime import date, timedelta

    AS_OF = date(2026, 11, 7)   # every "last N days" and "last month" below counts back from here

    # "Last month" is the last full calendar month before AS_OF: October 2026.
    _this_month_start = AS_OF.replace(day=1)
    LAST_MONTH_START = (_this_month_start - timedelta(days=1)).replace(day=1)
    LAST_MONTH_END = _this_month_start   # exclusive: up to, not including, this month

    LAST_60_START = AS_OF - timedelta(days=60)

    AS_OF, LAST_MONTH_START, LAST_MONTH_END, LAST_60_START
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            (SELECT count(*) FROM order_line)   AS n_order_lines,
            (SELECT count(*) FROM line_option)   AS n_line_options,
            (SELECT count(DISTINCT line_id) FROM line_option) AS lines_with_options
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Business questions**

    1. The three best-selling products last month, by units.

    2. Revenue, cost and margin by menu category, with what the options earned counted in, each option under the category of the product on its line. (three tables or more)

    3. For each member: the number of orders, the total spent and the average order, keeping the members whose total spent is above the members' average. (three tables or more)

    4. Every order's payments checked against its total, and a list of the orders where they do not match. (three tables or more) (checks a rule)

    5. The members who joined and have never ordered.

    6. The share of orders paid at least partly with points, for each month.

    7. The products, available today or not, that have not sold in the last 60 days.

    8. The product that generate the highest gross profit (including options within their lines total)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **How I Know These Numbers Are Right**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Working With the Agent**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Reading It Back**
    how many rows you expect its joins to produce before any grouping, and why?

    Chosen question: Q4. Every order's payments checked against its total, and a list of the orders where they do not match. (three tables or more) (checks a rule)

    Prediction: 1,287 rows (after first grouping but before final grouping)

    and reasoning:
    this question needs 2 steps processing
    1. adding up each order’s lines and their options (order_line + line_option) into one total per order --> 1200 rows equals to order's rows, as we're joining order_lines into it
    2. joining the result from step 1 to the payment table. each payment belongs to exactly one order, so no payment is lost or doubled --> 1287 rows equals to the payment rows

    then after that we group them into ones that match and don't match the order total
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Going Further.**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Time Spent**
    """)
    return


if __name__ == "__main__":
    app.run()
