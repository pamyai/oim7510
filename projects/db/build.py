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

    return ask, database


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The Tables**
    """)
    return


@app.cell
def _(database, duckdb):
    database.unlink(missing_ok=True)

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
    return


@app.cell
def _(ask):
    ask("SHOW ALL TABLES")
    return


if __name__ == "__main__":
    app.run()
