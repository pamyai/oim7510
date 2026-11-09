#try1
import marimo

app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import duckdb
    return duckdb, mo


@app.cell
def _(duckdb, mo):

database = mo.notebook_dir() / "database.duckdb"

def ask(sql):
    with duckdb.connect(database, read_only=True) as _con:
        return _con.sql(sql).pl()
        