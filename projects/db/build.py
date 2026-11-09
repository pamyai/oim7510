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
    **The Tables**
    """)
    return


app._unparsable_cell(
    r"""
    database.unlink(missing_ok=True)
    with duckdb.connect(database) as _con:

    """,
    name="_"
)


if __name__ == "__main__":
    app.run()
