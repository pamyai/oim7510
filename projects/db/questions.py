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
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
