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

        # A view for a question the café asks every week: for each order, what the
        # lines and options were charged (order_total) against what was actually
        # paid (paid_total). Saved as a view, so anybody can ask for it by name
        # and always get the current rows, instead of re-writing this join.
        _con.sql("""
        CREATE VIEW order_totals AS
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
               o.order_datetime,
               o.member_id,
               o.order_channel,
               lt.lines_total,
               COALESCE(ot.options_total, 0) AS options_total,
               lt.lines_total + COALESCE(ot.options_total, 0) AS order_total,
               COALESCE(pt.paid_total, 0) AS paid_total
        FROM orders o
        JOIN line_totals lt ON lt.order_id = o.order_id
        LEFT JOIN option_totals ot ON ot.order_id = o.order_id
        LEFT JOIN pay_totals pt ON pt.order_id = o.order_id
        """)
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
def _(mo):
    mo.md(r"""
    **A Look at the Data**
    """)
    return


@app.cell
def _(mo, pl):
    import altair as alt

    _orders_df = pl.read_csv(mo.notebook_dir() / "data" / "orders.csv", try_parse_dates=True)
    _by_hour = (
        _orders_df
        .with_columns(pl.col("order_datetime").dt.hour().alias("hour"))
        .group_by("hour")
        .len()
        .sort("hour")
    )

    alt.Chart(_by_hour).mark_bar().encode(
        x=alt.X("hour:O", title="Hour of day"),
        y=alt.Y("len:Q", title="Number of orders"),
        tooltip=["hour", "len"],
    ).properties(title="Orders by hour of day", width=400, height=300)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Orders peak at 8–9am and again at noon, with a dip around 11am and a decline
    through the afternoon — a believable shape for a campus café, so nothing in
    `make_data.py` needed changing.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Row Counts**
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT 'member' AS table_name, count(*) AS n_rows FROM member
        UNION ALL SELECT 'menu', count(*) FROM menu
        UNION ALL SELECT 'options', count(*) FROM options
        UNION ALL SELECT 'orders', count(*) FROM orders
        UNION ALL SELECT 'order_line', count(*) FROM order_line
        UNION ALL SELECT 'line_option', count(*) FROM line_option
        UNION ALL SELECT 'payment', count(*) FROM payment
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **A Row It Refuses**

    An order's payments must each be a positive amount (`payment_amt > 0`). The insert
    below tries to record a payment of $0, which the table's CHECK constraint refuses.
    """)
    return


@app.cell
def _(database, duckdb):
    try:
        with duckdb.connect(database) as _con:
            _con.sql("""
                INSERT INTO payment (payment_id, order_id, payment_method, payment_amt)
                VALUES (99999, 1, 'cash', 0)
            """)
        print("Insert succeeded (unexpected).")
    except Exception as _e:
        print("The database refused the row:")
        print(_e)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Answers You Already Knew**

    Three things I expected before running the query, because I know what
    `make_data.py` was told to generate.

    1. **Members who never ordered.** `make_data.py` sets aside member IDs 46–50
       as members who joined but never placed an order — so I expect exactly 5 rows.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT count(*) AS members_never_ordered
        FROM member m
        WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.member_id = m.member_id)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    2. **Duplicate first names.** `make_data.py` lists two members named "Emma" and
       two named "Sam" on purpose, to show that a name is not a key — so I expect
       exactly 2 rows for each of those two names.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT member_name, count(*) AS n_members
        FROM member
        WHERE member_name IN ('Emma', 'Sam')
        GROUP BY member_name
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    3. **Orders with no member.** Walk-in customers who are not loyalty members
       buy too, and `make_data.py` only picks a member for a fraction of orders
       (55% on the app, 35% at the counter) — so I expect a few hundred orders,
       not all 1,200, to have no member_id.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT count(*) AS orders_no_member
        FROM orders
        WHERE member_id IS NULL
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **A View**

    The café asks every week whether every order's payments add up to what it was
    charged — its lines and their options together. That rule spans three tables
    (`order_line`, `line_option` and `payment`), so no single CHECK constraint can
    hold it. The view `order_totals`, created in The Tables above, answers it by
    name: anybody can ask for it and always get the current rows, instead of
    re-writing the join. Part B's rule-checking question uses this view.
    """)
    return


if __name__ == "__main__":
    app.run()
