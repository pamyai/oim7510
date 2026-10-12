# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of option, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    *Who would use this, and what decision does it help them make? Two or three sentences, in words somebody outside this course would understand.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Reorder simulation can be used by any small business owner / warehouse / inventory managers with a simple supply chain / stock flow that has any cost associated with holding, ordering, or stockouts of inventory. It helps determine stock ROP (Reorder Point) based on demand variability, lead time, and desired service level if applicable.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    *Before you ask your agent anything, write how you would solve it: the steps, in order, in plain words, in five lines or more. Then answer these two questions:*

    - *What does your loop carry from one step to the next, the way a running total carries its sum?*
    - *Which check will you use in section 6, and which two numbers should agree?*

    *Commit this notebook with the message `mp1: plan before AI`.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    steps
    1. Declare list of reorder_points = [20, 30, 40, 50].
    2. For each reorder point:
    - Set inventory = 60.
    - Create an empty list of outstanding orders (orders placed but not yet delivered).
    - Create variables/lists to track lost sales, orders placed, ending stock, etc.
    3. For each day:
    - Check whether any order is due to arrive today. If yes, add it to inventory and remove it from outstanding orders.
    - Record the day's starting inventory.
    4. Process demand:
    - If inventory is at least demand, sell all demand.
    - Else, sell all remaining inventory, set inventory to 0, and record the unmet demand as lost sales.
    5. Calculate ending inventory.
    6. inventory position = ending inventory + all outstanding orders.
    7. If inventory position is less than or equal to the reorder point:
    Place an order for 100 cartons.
    Schedule it to arrive 3 days later.
    Save the day's results.
    8. Move to the next day, carrying forward the updated inventory and outstanding orders.
    9. After 30 days, calculate total units lost, days with lost sales, number of orders placed, and average ending inventory.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. What does your loop carry from one step to the next, the way a running total carries its sum?

    The loop
    - Carries the current inventory level and any outstanding orders that have been placed but not yet delivered.
    - Updates running totals of lost sales, orders placed, and ending inventory as it moves from one day to the next.

    2. Which check will you use in section 6, and which two numbers should agree?

    Total Demand = Total Sold + Total Lost Sales
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your option from the Mini Project 1 page. If you chose D, your own option, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    starting_stock = 60
    order_quantity = 100
    lead_time_days = 3
    reorder_points = [20, 30, 40, 50]
    daily_demand = [12, 15, 9, 14, 18, 11, 10, 16, 13, 17, 8, 12, 20, 14, 11,
                    9, 15, 13, 16, 12, 10, 14, 19, 11, 13, 15, 9, 12, 17, 14]
    return (
        daily_demand,
        lead_time_days,
        order_quantity,
        reorder_points,
        starting_stock,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _(daily_demand, lead_time_days, order_quantity, starting_stock):
    #try with ROP = 40
    reorder_point_40 = 40
    stock = starting_stock
    outstanding_orders = []  # list of (arrival_day, quantity) tuples: orders placed but not yet delivered
    day_table = []           # one row per day: (day, starting stock, arrived, demand, sold, lost, ending stock, units ordered)

    for day in range(30):
        starting_today = stock

        # 1. deliver any order whose arrival day is today
        arrived = 0
        still_outstanding = []
        for arrival_day, qty in outstanding_orders:
            if arrival_day == day:
                arrived = arrived + qty
            else:
                still_outstanding.append((arrival_day, qty))
        outstanding_orders = still_outstanding
        stock = stock + arrived

        # 2. sell what demand asks for, up to what is on the shelf
        demand = daily_demand[day]
        if stock >= demand:
            sold = demand
            lost = 0
        else:
            sold = stock
            lost = demand - stock
        stock = stock - sold
        ending = stock

        # 3. inventory position = ending stock plus whatever is still on order
        outstanding_qty = 0
        for arrival_day, qty in outstanding_orders:
            outstanding_qty = outstanding_qty + qty
        inventory_position = ending + outstanding_qty

        # 4. reorder if the position has fallen to or below the reorder point
        units_ordered = 0
        if inventory_position <= reorder_point_40:
            outstanding_orders.append((day + lead_time_days, order_quantity))
            units_ordered = order_quantity

        day_table.append((day + 1, starting_today, arrived, demand, sold, lost, ending, units_ordered))

    day_table[0] #check result 
    return (day_table,)


@app.cell
def _(day_table):
    print(f"{'day':>4} {'start':>6} {'arrived':>8} {'demand':>7} {'sold':>5} {'lost':>5} {'end':>6} {'ordered':>8}")
    for day_num, start, arrived_qty, demand_qty, sold_qty, lost_qty, end, ordered_qty in day_table:
        print(f"{day_num:>4} {start:>6} {arrived_qty:>8} {demand_qty:>7} {sold_qty:>5} {lost_qty:>5} {end:>6} {ordered_qty:>8}")
    return


@app.cell
def _(
    daily_demand,
    lead_time_days,
    order_quantity,
    reorder_points,
    starting_stock,
):
    # run the same simulation for every reorder point, saving one summary row for each
    comparison_table = []   # one row per reorder point: (reorder point, units lost, days with a lost sale, orders placed, average ending stock)

    for rp in reorder_points:
        current_stock = starting_stock
        current_outstanding = []   # list of (arrival_day, quantity) tuples: orders placed but not yet delivered

        rp_units_lost = 0
        rp_days_with_lost_sale = 0
        rp_orders_placed = 0
        rp_ending_stock_sum = 0

        for today in range(30):
            # 1. deliver any order whose arrival day is today
            today_arrived = 0
            still_waiting = []
            for order_arrival_day, order_qty in current_outstanding:
                if order_arrival_day == today:
                    today_arrived = today_arrived + order_qty
                else:
                    still_waiting.append((order_arrival_day, order_qty))
            current_outstanding = still_waiting
            current_stock = current_stock + today_arrived

            # 2. sell what demand asks for, up to what is on the shelf
            today_demand = daily_demand[today]
            if current_stock >= today_demand:
                today_sold = today_demand
                today_lost = 0
            else:
                today_sold = current_stock
                today_lost = today_demand - current_stock
            current_stock = current_stock - today_sold
            rp_units_lost = rp_units_lost + today_lost
            if today_lost > 0:
                rp_days_with_lost_sale = rp_days_with_lost_sale + 1
            rp_ending_stock_sum = rp_ending_stock_sum + current_stock

            # 3. inventory position = ending stock plus whatever is still on order
            still_on_order = 0
            for order_arrival_day, order_qty in current_outstanding:
                still_on_order = still_on_order + order_qty
            today_inventory_position = current_stock + still_on_order

            # 4. reorder if the position has fallen to or below the reorder point
            if today_inventory_position <= rp:
                current_outstanding.append((today + lead_time_days, order_quantity))
                rp_orders_placed = rp_orders_placed + 1

        rp_average_ending_stock = rp_ending_stock_sum / 30
        comparison_table.append((rp, rp_units_lost, rp_days_with_lost_sale, rp_orders_placed, rp_average_ending_stock))

    comparison_table
    return (comparison_table,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _(comparison_table):
    print(f"{'reorder pt':>10} {'units lost':>10} {'days w/ lost sale':>17} {'orders placed':>14} {'avg end stock':>14}")
    for rp_value, rp_lost, rp_days_lost, rp_orders, rp_avg_end in comparison_table:
        print(f"{rp_value:>10} {rp_lost:>10} {rp_days_lost:>17} {rp_orders:>14} {rp_avg_end:>14.1f}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    A reorder point of 40 is recommended: it is the lowest reorder point that avoids any lost sales (0 units lost over 30 days), while carrying less average stock (48.4 units) than reorder point 50 (58.4 units), which has the same zero lost sales.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell(hide_code=True)
def _(
    daily_demand,
    lead_time_days,
    order_quantity,
    reorder_points,
    starting_stock,
):
    # Check: total demand should equal total sold plus total lost sales, for every reorder point.
    # This reruns the simulation independently, tracking sold and lost separately, to see if they add back up to demand.
    check_results = []   # one row per reorder point: (reorder point, total demand, total sold, total lost, do they match)

    for check_rp in reorder_points:
        check_stock = starting_stock
        check_outstanding = []   # list of (arrival_day, quantity) tuples: orders placed but not yet delivered

        check_total_demand = 0
        check_total_sold = 0
        check_total_lost = 0

        for check_day in range(30):
            # deliver any order whose arrival day is today
            check_arrived = 0
            check_still_waiting = []
            for check_arrival_day, check_qty in check_outstanding:
                if check_arrival_day == check_day:
                    check_arrived = check_arrived + check_qty
                else:
                    check_still_waiting.append((check_arrival_day, check_qty))
            check_outstanding = check_still_waiting
            check_stock = check_stock + check_arrived

            # sell what demand asks for, up to what is on the shelf
            check_demand = daily_demand[check_day]
            check_total_demand = check_total_demand + check_demand
            if check_stock >= check_demand:
                check_sold = check_demand
                check_lost = 0
            else:
                check_sold = check_stock
                check_lost = check_demand - check_stock
            check_stock = check_stock - check_sold
            check_total_sold = check_total_sold + check_sold
            check_total_lost = check_total_lost + check_lost

            # inventory position = stock on hand plus stock still on order
            check_still_on_order = 0
            for check_arrival_day, check_qty in check_outstanding:
                check_still_on_order = check_still_on_order + check_qty
            check_inventory_position = check_stock + check_still_on_order

            # reorder if the position has fallen to or below the reorder point
            if check_inventory_position <= check_rp:
                check_outstanding.append((check_day + lead_time_days, order_quantity))

        check_sold_plus_lost = check_total_sold + check_total_lost
        check_match = (check_total_demand == check_sold_plus_lost)
        check_results.append((check_rp, check_total_demand, check_total_sold, check_total_lost, check_match))

    print(f"{'reorder pt':>10} {'demand':>8} {'sold':>6} {'lost':>6} {'sold+lost':>10} {'match':>7}")
    for check_rp_value, check_demand_total, check_sold_total, check_lost_total, check_is_match in check_results:
        check_total = check_sold_total + check_lost_total
        print(f"{check_rp_value:>10} {check_demand_total:>8} {check_sold_total:>6} {check_lost_total:>6} {check_total:>10} {str(check_is_match):>7}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


app._unparsable_cell(
    r"""
    The first cell of section 4, ai kept trying to generate new reorder point as new list of different numbers. I had to keep reminding it to just pull the input from the previous cell.

    I verified results by manually calculating results if the first 2 days of ROP = 40 see if it match. 
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Experiment 1: Full-year demand.

    I tried generating a full year (365 days) of random daily demand instead of the fixed 30-day list, to see if reorder point 40 still holds up over a longer, noisier stretch of time.
    """)
    return


@app.cell
def _():
    import random

    # a fixed seed makes the "random" numbers the same every time this cell runs
    random.seed(42)

    year_demand = []
    for _ in range(365):
        year_demand.append(random.randint(8, 20))   # same range as the original 30-day demand numbers

    year_demand[:10]   # peek at the first 10 days
    return (year_demand,)


@app.cell
def _(
    lead_time_days,
    order_quantity,
    reorder_points,
    starting_stock,
    year_demand,
):
    # rerun the same simulation logic as the comparison table, but over 365 days of random demand instead of 30 fixed days
    year_comparison_table = []   # one row per reorder point: (reorder point, units lost, days with a lost sale, orders placed, average ending stock)

    for year_rp in reorder_points:
        year_stock = starting_stock
        year_outstanding = []   # list of (arrival_day, quantity) tuples: orders placed but not yet delivered

        year_units_lost = 0
        year_days_with_lost_sale = 0
        year_orders_placed = 0
        year_ending_stock_sum = 0

        for year_day in range(365):
            # 1. deliver any order whose arrival day is today
            year_arrived = 0
            year_still_waiting = []
            for year_arrival_day, year_qty in year_outstanding:
                if year_arrival_day == year_day:
                    year_arrived = year_arrived + year_qty
                else:
                    year_still_waiting.append((year_arrival_day, year_qty))
            year_outstanding = year_still_waiting
            year_stock = year_stock + year_arrived

            # 2. sell what demand asks for, up to what is on the shelf
            year_demand_today = year_demand[year_day]
            if year_stock >= year_demand_today:
                year_sold = year_demand_today
                year_lost = 0
            else:
                year_sold = year_stock
                year_lost = year_demand_today - year_stock
            year_stock = year_stock - year_sold
            year_units_lost = year_units_lost + year_lost
            if year_lost > 0:
                year_days_with_lost_sale = year_days_with_lost_sale + 1
            year_ending_stock_sum = year_ending_stock_sum + year_stock

            # 3. inventory position = ending stock plus whatever is still on order
            year_still_on_order = 0
            for year_arrival_day, year_qty in year_outstanding:
                year_still_on_order = year_still_on_order + year_qty
            year_inventory_position = year_stock + year_still_on_order

            # 4. reorder if the position has fallen to or below the reorder point
            if year_inventory_position <= year_rp:
                year_outstanding.append((year_day + lead_time_days, order_quantity))
                year_orders_placed = year_orders_placed + 1

        year_average_ending_stock = year_ending_stock_sum / 365
        year_comparison_table.append((year_rp, year_units_lost, year_days_with_lost_sale, year_orders_placed, year_average_ending_stock))

    print(f"{'reorder pt':>10} {'units lost':>10} {'days w/ lost sale':>17} {'orders placed':>14} {'avg end stock':>14}")
    for year_rp_value, year_lost_total, year_days_lost_total, year_orders_total, year_avg_end in year_comparison_table:
        print(f"{year_rp_value:>10} {year_lost_total:>10} {year_days_lost_total:>17} {year_orders_total:>14} {year_avg_end:>14.1f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    result shows more lost sales from ROP = 40. in this case it might be up to operator's policy whether to prioritize reducing lost sales or minimizing inventory holding costs when deciding the appropriate reorder point. Otherwise they might have to calculate proper holding cost and lost sales cost to find the optimal balance between the two.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Experiment2: Conduct linear programming model to find new reorder point that will give lost sales = 0 according to this new data set
    """)
    return


if __name__ == "__main__":
    app.run()
