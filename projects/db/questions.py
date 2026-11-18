#try1

import marimo

__generated_with = "0.24.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    import altair as alt

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
    as_of = "2026-11-07"
    return (as_of,)


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
    # Q1. The three best-selling products last month, by units.
    """)
    return


@app.cell
def _(as_of, ask):
    ask(f"""
        SELECT m.prod_name, m.prod_cat, sum(ol.line_qty) AS units_sold
        FROM orders o
        JOIN order_line ol ON ol.order_id = o.order_id
        JOIN menu m        ON m.prod_id   = ol.prod_id
        WHERE o.order_datetime >= date_trunc('month', DATE '{as_of}') - INTERVAL 1 MONTH
          AND o.order_datetime <  date_trunc('month', DATE '{as_of}')
        GROUP BY m.prod_name, m.prod_cat
        ORDER BY units_sold DESC
        LIMIT 3
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In October 2026, the last full month before the as_of date, the three best sellers
    were all coffee: the Latte with 24 units, the Americano with 19 and the Cold Brew
    with 17. The next product, the Iced Latte, sold 16, so there is no tie for third place.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. How much revenue, cost and margin does each menu category bring in, counting the add-on options?
    """)
    return


@app.cell
def _(ask):

    ask("""
        WITH sales AS (
            SELECT m.prod_cat                  AS category,
                   ol.line_qty * ol.line_price AS revenue,
                   ol.line_qty * m.prod_cost   AS cost
            FROM order_line ol
            JOIN menu m ON m.prod_id = ol.prod_id
            UNION ALL
            SELECT m.prod_cat,
                   ol.line_qty * lo.option_price_charged,
                   ol.line_qty * op.option_cost
            FROM line_option lo
            JOIN order_line ol ON ol.line_id   = lo.line_id
            JOIN menu m        ON m.prod_id    = ol.prod_id
            JOIN options op    ON op.option_id = lo.option_id
        )
        SELECT category,
               sum(revenue)             AS revenue,
               sum(cost)                AS cost,
               sum(revenue) - sum(cost) AS margin,
               round(100 * (sum(revenue) - sum(cost)) / sum(revenue), 1) AS margin_pct
        FROM sales
        GROUP BY category
        ORDER BY margin DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Over the 12 months of data, coffee earns the most: $5,273.50 in revenue and a
    $4,007.85 margin (76.0%). It is followed by tea ($1,369.00, 75.8%), food
    ($1,338.80, 67.5%) and other drinks ($333.80, 64.4%). Revenue across all four
    categories adds up to $9,579.50. I read "cost" as the menu's current cost for
    each product and option, since the café does not keep a history of its costs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. Which loyalty members spend more than the average member, and how often and how much do they order?
    """)
    return


@app.cell
def _(ask):
    ask("""
        WITH per_member AS (
            SELECT mb.member_id, mb.member_name,
                   count(*)                     AS n_orders,
                   sum(t.order_total)           AS total_spent,
                   round(avg(t.order_total), 2) AS avg_order
            FROM member mb
            JOIN order_totals t ON t.member_id = mb.member_id
            GROUP BY mb.member_id, mb.member_name
        )
        SELECT *
        FROM per_member
        WHERE total_spent > (SELECT avg(total_spent) FROM per_member)
        ORDER BY total_spent DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    21 of the 45 members who have ordered spent more than the members' average. The
    top spender is Tara (member 20) with $181.75 over 23 orders, an average order of
    $7.90, followed by Aisha (member 1) with $178.00 over 19 orders. "Total spent" is
    what the member's lines and options were charged (the café's revenue), not what
    they paid. The average is taken over the members who have ordered at least once,
    so the five members who never ordered do not pull it down.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4. Do every order's payments add up to the order's total, and which orders don't match?
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT order_id, order_datetime, member_id, order_total, paid_total,
               paid_total - order_total AS difference
        FROM order_totals
        WHERE paid_total <> order_total
        ORDER BY order_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exactly two of the 1,200 orders break the rule, and they are the two I broke on
    purpose in Part A. Order 501 (April 4, 2026) cost $13.00 but was paid $14.50,
    which is $1.50 too much. Order 667 (May 12, 2026) cost $4.25 but was paid $3.25,
    which is $1.00 too little.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 5. Which loyalty members signed up but have never placed an order?
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT mb.member_id, mb.member_name, mb.member_join_date
        FROM member mb
        LEFT JOIN orders o ON o.member_id = mb.member_id
        WHERE o.order_id IS NULL
        ORDER BY mb.member_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Five members have never ordered: Emma (46), Leo (47), Mia (48), Sam (49) and
    Ana (50). Sam and Ana joined in the last two weeks, on October 26 and November 2,
    2026, so they may simply not have come in yet. Emma, Leo and Mia joined months ago,
    so they are the ones to win back.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 6. Each month, what share of orders was paid at least partly with loyalty points?
    """)
    return


@app.cell
def _(ask):
    points_by_month = ask("""
        WITH per_order AS (
            SELECT o.order_id,
                   date_trunc('month', o.order_datetime) AS month,
                   bool_or(p.payment_method = 'points')  AS used_points
            FROM orders o
            JOIN payment p ON p.order_id = o.order_id
            GROUP BY o.order_id, month
        )
        SELECT strftime(month, '%Y-%m')            AS month,
               count(*)                            AS n_orders,
               count(*) FILTER (WHERE used_points) AS n_with_points,
               round(100 * count(*) FILTER (WHERE used_points) / count(*), 1) AS pct_with_points
        FROM per_order
        GROUP BY month
        ORDER BY month
    """)
    points_by_month
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Across the year, 102 of the 1,200 orders (8.5%) were paid at least partly with
    points. The share moves between 4.0% (December 2025) and 13.7% (June 2026), and
    was 4.7% in October 2026. November 2025 and November 2026 are partial months,
    because the data starts on November 8, 2025 and ends on the as_of date,
    November 7, 2026.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 7. Which menu products, available today or not, have not sold in the last 60 days?
    """)
    return


@app.cell
def _(as_of, ask):
    ask(f"""
        SELECT m.prod_id, m.prod_name, m.prod_cat, m.prod_avail,
               max(o.order_datetime)::DATE AS last_sold
        FROM menu m
        LEFT JOIN order_line ol ON ol.prod_id = m.prod_id
        LEFT JOIN orders o      ON o.order_id = ol.order_id
        GROUP BY m.prod_id, m.prod_name, m.prod_cat, m.prod_avail
        HAVING max(o.order_datetime) IS NULL
            OR max(o.order_datetime) < DATE '{as_of}' - INTERVAL 59 DAY
        ORDER BY m.prod_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two of the 23 products have not sold in the 60 days from September 9 to
    November 7, 2026. The Pumpkin Spice Latte, which is off the menu, last sold on
    December 12, 2025. The Ginger Scone is still listed as available but last sold on
    July 25, 2026, so the café might take it off the menu.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 8. My own question: Which products generate the highest gross profit, including the options sold on their lines?
    """)
    return


@app.cell
def _(ask):
    ask("""
        WITH line_profit AS (
            SELECT ol.line_id, ol.prod_id,
                   ol.line_qty * (ol.line_price - m.prod_cost) AS product_profit
            FROM order_line ol
            JOIN menu m ON m.prod_id = ol.prod_id
        ),
        option_profit AS (
            SELECT lo.line_id,
                   sum(ol.line_qty * (lo.option_price_charged - op.option_cost)) AS options_profit
            FROM line_option lo
            JOIN order_line ol ON ol.line_id   = lo.line_id
            JOIN options op    ON op.option_id = lo.option_id
            GROUP BY lo.line_id
        )
        SELECT m.prod_name, m.prod_cat,
               sum(lp.product_profit)                                  AS product_profit,
               sum(coalesce(op.options_profit, 0))                     AS options_profit,
               sum(lp.product_profit + coalesce(op.options_profit, 0)) AS gross_profit
        FROM line_profit lp
        JOIN menu m ON m.prod_id = lp.prod_id
        LEFT JOIN option_profit op ON op.line_id = lp.line_id
        GROUP BY m.prod_name, m.prod_cat
        ORDER BY gross_profit DESC
        LIMIT 5
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The Latte generates the most gross profit over the year: $890.35, of which $841.75
    comes from the drink itself and $48.60 from the options added to it. That is about
    $300 more than the next product, the Iced Latte, at $592.25. Four of the top five
    are coffee drinks; the fifth is the Chai Latte, at $526.40.
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
    Check 1: question 2's revenue, reached another way.** Question 2 adds up
    revenue line by line and option by option, by category. The `order_totals` view
    adds it up order by order, without categories. Both should come to the same total.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            (SELECT sum(ol.line_qty * ol.line_price) FROM order_line ol)
          + (SELECT sum(ol.line_qty * lo.option_price_charged)
               FROM line_option lo JOIN order_line ol ON ol.line_id = lo.line_id)
                                                      AS q2_revenue_all_categories,
            (SELECT sum(order_total) FROM order_totals) AS revenue_order_by_order,
            (SELECT sum(payment_amt) FROM payment)      AS payments_received
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
