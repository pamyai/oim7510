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

    return duckdb, mo, pl


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return ask, database


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The Tables**
    """)
    return


@app.cell
def _(database, duckdb, mo):
    database.unlink(missing_ok=True)
    _data_dir = mo.notebook_dir() / "data"

    with duckdb.connect(database) as _con:
        _con.sql("""
        CREATE TABLE member (
            member_id        INTEGER PRIMARY KEY,
            member_name      VARCHAR NOT NULL,
            member_mobile    VARCHAR NOT NULL UNIQUE,
            member_email     VARCHAR,                          -- optional
            member_join_date DATE NOT NULL,
            member_points    INTEGER NOT NULL DEFAULT 0 CHECK (member_points >= 0)
        );

        CREATE TABLE menu (
            prod_id    INTEGER PRIMARY KEY,
            prod_name  VARCHAR NOT NULL UNIQUE,
            prod_cat   VARCHAR NOT NULL CHECK (prod_cat IN ('coffee', 'tea', 'food', 'other')),
            prod_price DECIMAL(6,2) NOT NULL,
            prod_cost  DECIMAL(6,2) NOT NULL CHECK (prod_cost >= 0),
            prod_avail BOOLEAN NOT NULL DEFAULT TRUE,
            CHECK (prod_price >= prod_cost)
        );

        CREATE TABLE options (
            option_id    INTEGER PRIMARY KEY,
            option_name  VARCHAR NOT NULL UNIQUE,
            option_price DECIMAL(6,2) NOT NULL CHECK (option_price >= 0),  -- can be zero
            option_cost  DECIMAL(6,2) NOT NULL CHECK (option_cost >= 0)
        );

        CREATE TABLE orders (
            order_id       INTEGER PRIMARY KEY,
            member_id      INTEGER REFERENCES member (member_id),  -- NULL = not a member
            order_datetime TIMESTAMP NOT NULL,
            order_channel  VARCHAR NOT NULL CHECK (order_channel IN ('counter', 'app'))
        );

        CREATE TABLE order_line (
            line_id    INTEGER PRIMARY KEY,
            order_id   INTEGER NOT NULL REFERENCES orders (order_id),
            prod_id    INTEGER NOT NULL REFERENCES menu (prod_id),
            line_qty   INTEGER NOT NULL CHECK (line_qty > 0),
            line_price DECIMAL(6,2) NOT NULL CHECK (line_price >= 0)
        );

        CREATE TABLE line_option (
            line_id              INTEGER NOT NULL REFERENCES order_line (line_id),
            option_id            INTEGER NOT NULL REFERENCES options (option_id),
            option_price_charged DECIMAL(6,2) NOT NULL CHECK (option_price_charged >= 0),
            PRIMARY KEY (line_id, option_id)   -- an option at most once per line
        );

        CREATE TABLE payment (
            payment_id     INTEGER PRIMARY KEY,
            order_id       INTEGER NOT NULL REFERENCES orders (order_id),
            payment_method VARCHAR NOT NULL CHECK (payment_method IN ('cash', 'card', 'app', 'points')),
            payment_amt    DECIMAL(8,2) NOT NULL CHECK (payment_amt > 0)
        );
        """)

        # Load each CSV straight into its table. read_csv_auto looks at the file
        # and guesses each column's type (number, date, text); the order below
        # follows the foreign keys, so every row a table points to already exists.
        for _name in ["member", "menu", "options", "orders", "order_line", "line_option", "payment"]:
            _path = str(_data_dir / f"{_name}.csv").replace("\\", "/")
            _con.sql(f"INSERT INTO {_name} SELECT * FROM read_csv_auto('{_path}')")
    return


@app.cell
def _(ask):
    ask("SHOW ALL TABLES")  # refreshed after loading data
    return


@app.cell
def _(ask):
    ask("SELECT count(*) AS n_orders FROM orders")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The Data**
    """)
    return


@app.cell
def _(mo):
    sorted(p.name for p in (mo.notebook_dir() / "data").glob("*.csv"))
    return


@app.cell
def _(mo, pl):
    _data_dir = mo.notebook_dir() / "data"
    for _name in ["member", "menu", "options", "orders", "order_line", "line_option", "payment"]:
        _df = pl.read_csv(_data_dir / f"{_name}.csv")
        print(_name, _df.columns)
    return


@app.cell
def _(ask):
    ask("""
        WITH line_totals AS (
            SELECT ol.order_id,
                   SUM(ol.line_qty * ol.line_price) AS lines_total
            FROM order_line ol
            GROUP BY ol.order_id
        ),
        option_totals AS (
            SELECT ol.order_id,
                   SUM(ol.line_qty * lo.option_price_charged) AS options_total
            FROM order_line ol
            JOIN line_option lo ON lo.line_id = ol.line_id
            GROUP BY ol.order_id
        ),
        pay_totals AS (
            SELECT order_id, SUM(payment_amt) AS paid_total
            FROM payment
            GROUP BY order_id
        )
        SELECT o.order_id,
               lt.lines_total,
               COALESCE(ot.options_total, 0) AS options_total,
               lt.lines_total + COALESCE(ot.options_total, 0) AS order_total,
               COALESCE(pt.paid_total, 0) AS paid_total
        FROM orders o
        JOIN line_totals lt ON lt.order_id = o.order_id
        LEFT JOIN option_totals ot ON ot.order_id = o.order_id
        LEFT JOIN pay_totals pt ON pt.order_id = o.order_id
        WHERE ABS(lt.lines_total + COALESCE(ot.options_total, 0) - COALESCE(pt.paid_total, 0)) > 0.01
    """)
    return


if __name__ == "__main__":
    app.run()
