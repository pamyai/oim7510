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

    return alt, duckdb, mo


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

    8. My own question: How many orders, and how much money, does the café take through each payment method?
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
    return (points_by_month,)


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
    # 8. My own question: How much money, does the café take through each payment method?
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT payment_method,
               count(*)                 AS n_payments,
               sum(payment_amt)         AS total_amount,
               round(100 * sum(payment_amt) / sum(sum(payment_amt)) OVER (), 1) AS pct_of_amount
        FROM payment
        GROUP BY payment_method
        ORDER BY total_amount DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Card brings in the most: 595 payments worth $4,631.25 (48.3% of all money taken),
    followed by the app (342 payments, $2,594.25, 27.1%) and cash (248 payments,
    $2,066.25, 21.6%). Points cover only $288.25 (3.0%) across 102 payments. Together,
    the 1,287 payments add up to $9,580.00.
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
    **Check 1:** question 2's revenue, reached another way.** Question 2 adds up
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
    Both ways give $9,579.50, which also matches the four categories in question 2
    added up by hand ($5,273.50 + $1,805.75 + $1,982.25 + $518.00). The payments come to
    $9,580.00, which is $0.50 more. That is exactly question 4's two broken orders
    together: +$1.50 on order 501 and −$1.00 on order 667.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Check 2:** question 5's count, reached another way.** Instead of looking for members
    with no matching order, count the members who do appear in orders and subtract that
    from all members.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            (SELECT count(*) FROM member)                  AS all_members,
            (SELECT count(DISTINCT member_id) FROM orders) AS members_who_ordered,
            (SELECT count(*) FROM member)
              - (SELECT count(DISTINCT member_id) FROM orders) AS never_ordered
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    50 − 45 = 5, the same five members as in question 5. That is also what
    `make_data.py` was told to make: members 46 to 50 never order.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Check 3: **question 6's counts, reached another way.** The monthly orders in
    question 6 should add up to every order, and the monthly points orders should add up
    to the number of orders with a points payment, counted straight from `payment`.
    """)
    return


@app.cell
def _(ask, points_by_month):
    ask("""
        SELECT
            (SELECT count(*) FROM orders) AS all_orders,
            (SELECT count(DISTINCT order_id) FROM payment
              WHERE payment_method = 'points') AS orders_with_points
    """), points_by_month.select("n_orders", "n_with_points").sum()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The 13 months add up to 1,200 orders and 102 orders with points, the same as
    counting them directly.
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
    when I tried query question 4, first ai didn't pre-aggregate anything, and just join orders → order_line → line_option → payment all at once. I redirect it to do 2-step join instead as it's more accurate and easier to track. The build section already made the joint order_total ready for use as well.
    See the Q4 query cell, and the order_totals view in build.py’s build cell.

    The rest of the work, AI got them right the first time. Samples of how I checked it are shown in How I Know These Numbers Are Right section
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


@app.cell
def _(ask):
    ask("""
        WITH order_total AS (
            SELECT ol.order_id,
                   sum(ol.line_qty * (ol.line_price + coalesce(lo.options, 0))) AS order_total
            FROM order_line ol
            LEFT JOIN (SELECT line_id, sum(option_price_charged) AS options
                       FROM line_option GROUP BY line_id) lo
                   ON lo.line_id = ol.line_id
            GROUP BY ol.order_id
        )
        SELECT
            (SELECT count(*) FROM order_total) AS step_1_rows,
            count(*)                           AS step_2_rows,
            count(DISTINCT t.order_id)         AS orders_in_step_2
        FROM order_total t
        JOIN payment p ON p.order_id = t.order_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Did it match?**

    Yes. Step 1 gives 1,200 rows, one per order, and the join to
    payments gives 1,287 rows, one per payment, as predicted. All 1,200 orders are still
    there after the join, so no payment was lost, and the count did not go above 1,287,
    so no payment was doubled. It matched because the order totals were added up
    *before* meeting the payments. Joining the raw lines to the payments instead would
    have paired every line of an order with every payment of that order, giving more
    rows and doubling the lines of the 87 orders paid in two parts.

    **What one row of the final result means:**

    one order whose payments do not match exactly to what the total of its lines and options were charged
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
    I tried two things. First, I put question 6 on a chart, to see whether points use
    has a season. Second, I added a dropdown, so a manager can pick any month and see
    that month's three best sellers (question 1) without editing the SQL.
    """)
    return


@app.cell
def _(alt, points_by_month):
    alt.Chart(points_by_month).mark_bar().encode(
        x=alt.X("month:O", title="Month"),
        y=alt.Y("pct_with_points:Q", title="Orders paid partly with points (%)"),
        tooltip=["month", "n_orders", "n_with_points", "pct_with_points"],
    ).properties(title="Share of orders paid at least partly with points", width=500, height=300)
    return


@app.cell
def _(mo, points_by_month):
    month_picker = mo.ui.dropdown(
        options=points_by_month["month"].to_list(),
        value="2026-10",
        label="Month",
    )
    month_picker
    return (month_picker,)


@app.cell
def _(ask, month_picker):
    ask(f"""
        SELECT m.prod_name, m.prod_cat, sum(ol.line_qty) AS units_sold
        FROM orders o
        JOIN order_line ol ON ol.order_id = o.order_id
        JOIN menu m        ON m.prod_id   = ol.prod_id
        WHERE strftime(o.order_datetime, '%Y-%m') = '{month_picker.value}'
        GROUP BY m.prod_name, m.prod_cat
        ORDER BY units_sold DESC
        LIMIT 3
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **What I found:** points use doesn't follow a clear season. It jumps around between
    4% and 14% from month to month, partly because the summer months have only about 50
    orders, so a few points orders move the share a lot. With the dropdown, picking
    2026-10 gives the same three products as question 1, which also checks that the
    control works.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Time Spent**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    5 hrs
    """)
    return


if __name__ == "__main__":
    app.run()
