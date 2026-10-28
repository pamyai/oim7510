import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #1. The Question

    The operations manager would use this tool to understand what happened in the business over the past week. It gives a quick view of sales, popular products, and any orders that still need attention.

    The tool helps the manager decide whether sales are performing well, which products are driving demand, and whether there are unshipped orders that need follow-up.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #2. My Plan Before AI

    steps:
    1. Calculate the date range for the last 7 days.
    2. Connect to the API and request all orders in that date range.
    3. Check pagination and keep requesting pages until all orders are collected.
    4. Loop through the orders to calculate total orders, total revenue, revenue by country, and unshipped orders.
    5. Connect to the API again for each order to get its line items.
    6. Loop through the line items to count units sold by product.
    7. Find the top 5 products.
    8. Build the report and write the manager summary sentence.


    questions:
    1. Which functions will your tool need? For each, what goes in and what comes out?

    suggested from the problem:
    - date.today()
    Input: none
    Output: today's date
    - timedelta(days=6)
    Input: number of days
    Output: a time difference used to calculate the start date
    - str(date)
    Input: a date object
    Output: a date string in the format YYYY-MM-DD
    - get_orders(from_date, to_date)
    Input: start date, end date
    Output: list of orders

    Additional:
    - get_order_details(order_id)
    Input: order ID
    Output: order line items
    - summarize_orders(orders)
    Input: list of orders
    Output:
    order count
    total revenue
    revenue by country
    unshipped orders
    - count_product_sales(order_details)
    Input: order line items
    Output: units sold by product
    - get_top_products(product_sales)
    Input: product sales totals
    Output: top 5 products

    2. Which addresses will they request?
    - /shop/orders to get all orders in the date range
    - /shop/orders/{order_id} to get the line items for each order
    3. How will you know you have every record?
    - Check the pagination information returned by the API.
    - Compare the number of orders collected with the total number of orders reported in pagination.
    - Continue requesting pages until those numbers match.
    4. Which check will you use in section 6, and which two numbers should agree?
    - A sum total amount from an order's line items should agree with the order’s total from /shop/orders.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #3. Inputs
    """)
    return


@app.cell
def _():
    days = 7
    base_url = "https://oim.zhili.dev/shop"
    return base_url, days


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #4. the work
    """)
    return


@app.cell
def _(days):
    #step1: date

    from datetime import date, timedelta

    to_date = date.today()
    from_date = to_date - timedelta(days=days - 1)

    print(f"Report covers {from_date} to {to_date}")
    return from_date, to_date


@app.cell
def _():
    #imports

    import requests

    return (requests,)


@app.cell
def _(base_url, requests):
    #step2-3: a function that fetches every order in a date range, page by page

    def get_orders(from_date, to_date):
        _orders = []
        _first_response = requests.get(f"{base_url}/orders", params={"from_date": str(from_date), "to_date": str(to_date)})
        _first_reply = _first_response.json()
        _total_pages = _first_reply['pagination']['pages']

        for _page in range(1, _total_pages + 1):
            _page_response = requests.get(f"{base_url}/orders", params={"from_date": str(from_date), "to_date": str(to_date), "page": _page})
            _page_reply = _page_response.json()
            for _order in _page_reply['items']:
                _orders.append(_order)

        return _orders, _first_reply['pagination']['total']

    return (get_orders,)


@app.cell
def _(from_date, get_orders, to_date):
    #call the function to get this week's orders

    orders, reported_total = get_orders(from_date, to_date)

    #check1: does the number of orders collected agree with the API's reported total?
    print(f"Collected {len(orders)} orders out of {reported_total} reported")
    return (orders,)


@app.cell
def _(orders):
    #save the fetched orders to a file, as the assignment requires

    import json
    import os

    os.makedirs("projects/mp2/data", exist_ok=True)

    with open("projects/mp2/data/orders.json", "w") as _file:
        json.dump(orders, _file, indent=2)

    print(f"Saved {len(orders)} orders to projects/mp2/data/orders.json")
    return (json,)


@app.cell
def _(orders):
    #step4: order count, total revenue, revenue by country, unshipped orders

    order_count = len(orders)
    total_revenue = 0
    revenue_by_country = {}
    unshipped_orders = []

    for _order in orders:
        total_revenue += _order['order_total_dollars']

        _country = _order['ship_country']
        if _country in revenue_by_country:
            revenue_by_country[_country] += _order['order_total_dollars']
        else:
            revenue_by_country[_country] = _order['order_total_dollars']

        if _order['shipped_date'] is None:
            unshipped_orders.append(_order)

    print(f"Order count: {order_count}")
    print(f"Total revenue: ${total_revenue:,.2f}")
    print(f"Unshipped orders: {len(unshipped_orders)}")
    return order_count, revenue_by_country, total_revenue, unshipped_orders


@app.cell
def _(base_url, requests):
    #step5a: a function that fetches one order's line items

    def get_order_details(order_id):
        _detail_response = requests.get(f"{base_url}/orders/{order_id}")
        _detail = _detail_response.json()
        return _detail['lines']


    return (get_order_details,)


@app.cell
def _(get_order_details, orders):
    #step5b: use the function to collect every order's line items

    order_lines = []

    for _order in orders:
        _lines = get_order_details(_order['order_id'])
        for _line in _lines:
            order_lines.append(_line)

    print(f"Collected {len(order_lines)} line items from {len(orders)} orders")
    return (order_lines,)


@app.cell
def _(json, order_lines):
    #save the fetched line items to a file too, as the assignment requires

    with open("projects/mp2/data/order_lines.json", "w") as _file:
        json.dump(order_lines, _file, indent=2)

    print(f"Saved {len(order_lines)} line items to projects/mp2/data/order_lines.json")
    return


@app.cell
def _(order_lines):
    #step6: units sold by product

    product_sales = {}

    for _line in order_lines:
        _product = _line['product_name']
        if _product in product_sales:
            product_sales[_product] += _line['quantity']
        else:
            product_sales[_product] = _line['quantity']

    print(f"Counted sales for {len(product_sales)} different products")
    return (product_sales,)


@app.cell
def _(product_sales):
    #step7: top 5 products

    picked_products = []
    top_products = []

    for _i in range(5):
        best_product = None
        best_count = -1
        for _product in product_sales:
            if _product not in picked_products and product_sales[_product] > best_count:
                best_count = product_sales[_product]
                best_product = _product
        top_products.append((best_product, best_count))
        picked_products.append(best_product)

    for _product, _count in top_products:
        print(f"{_product}: {_count} units")
    return picked_products, top_products


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #5. The Answer
    """)
    return


@app.cell
def _(top_products):
    #top 5 products, printed as a lined-up table

    print(f"{'Product':<40}{'Units sold':>12}")
    for _product, _count in top_products:
        print(f"{_product:<40}{_count:>12}")
    return


@app.cell
def _(revenue_by_country):
    #revenue by country, printed as a lined-up table

    print(f"{'Country':<20}{'Revenue':>15}")
    for _country in revenue_by_country:
        print(f"{_country:<20}{revenue_by_country[_country]:>15,.2f}")
    return


@app.cell
def _(to_date, unshipped_orders):
    #unshipped orders, printed as a lined-up table, with whether each is actually past its required ship date

    print(f"{'Order ID':<10}{'Order date':<20}{'Required date':<22}{'Country':<15}{'Order total':>12}  {'Late?'}")
    for _order in unshipped_orders:
        _is_late = str(_order['required_date']) < str(to_date)
        _late_flag = "LATE" if _is_late else "not yet due"
        print(f"{_order['order_id']:<10}{_order['order_date']:<20}{_order['required_date']:<22}{_order['ship_country']:<15}{_order['order_total_dollars']:>12,.2f}  {_late_flag}")
    return


@app.cell
def _(
    days,
    order_count,
    to_date,
    top_products,
    total_revenue,
    unshipped_orders,
):
    #one sentence for the manager

    _top_product, _top_count = top_products[0]
    print(f"In the {days} days ending {to_date}, Northwind received {order_count} orders worth ${total_revenue:,.2f}; {_top_product} was the top seller with {_top_count} units, and {len(unshipped_orders)} orders have not shipped yet.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #6. How I Know These Numbers Are Right

    I checked 5 things a second way, all shown in the cells below. The specific counts below are from when I ran this on Oct 28, 2026; since the API's data changes daily, running this notebook again on another day will show different counts, but the checks themselves will still agree with each other.

    **check1. Did I collect every order?**
    In step 3, the API's pagination reported a total number of orders in this date range. I collected orders page by page and compared the count in my `orders` list against that reported total. When I ran it on Oct 28, both came to 32, so I have every order, not just the first page.

    **check2. Does each order's line-item total agree with its reported order total?**
    An order's `order_total_dollars` (from `/shop/orders`) should equal the sum of its `line_total_dollars` values (from `/shop/orders/{order_id}`), since the order total is just all its lines added up. I checked this for every order collected: I summed each order's lines separately and compared that sum to the order's reported total, allowing a one-cent gap for rounding. When I ran it on Oct 28, 0 of 32 orders disagreed, so the revenue and line-item numbers in this report agree with each other.

    **check3. Did I collect every line item?**
    Each order in `/shop/orders` already reports its own `line_count`, a count of how many line items it has. I summed `line_count` across all orders and compared it to the number of line items I actually collected in step 5. When I ran it on Oct 28, both came to 1015, so step 6 and step 7, which depend on having every line item, are built on a complete set.

    **check4. Does the units-sold total in `product_sales` agree with the raw line items?**
    I summed the units two different ways: once by adding up every value already stored in the `product_sales` dictionary (built in step 6), and once by going back to `order_lines` directly and adding up every `quantity` field. When I ran it on Oct 28, both came to 24,764 units, so building the dictionary did not drop or double-count anything.

    **check5. Are the top 5 products really the top 5?**
    The picking method in step 7 works by repeatedly scanning for the highest remaining count, so it should be correct by construction, but I checked it a different way anyway: I took the 5th-place product's count and scanned every other product not in the top 5 to see if any of them actually sold more. When I ran it on Oct 28, none did, which confirms the top 5 list is right.
    """)
    return


@app.cell
def _(get_order_details, orders):
    #check2: does the sum of an order's lines agree with its order_total_dollars?

    mismatch_count = 0

    for _order in orders:
        _lines = get_order_details(_order['order_id'])

        _line_sum = 0
        for _line in _lines:
            _line_sum += _line['line_total_dollars']

        if abs(_line_sum - _order['order_total_dollars']) > 0.01:
            mismatch_count += 1
            print(f"Order {_order['order_id']}: lines sum to {_line_sum:.2f}, order total is {_order['order_total_dollars']:.2f}")

    print(f"Checked {len(orders)} orders, {mismatch_count} did not match")
    return


@app.cell
def _(order_lines, orders):
    #check3: does the number of line items we collected agree with the API's own line_count for each order?

    total_line_count_reported = 0
    for _order in orders:
        total_line_count_reported += _order['line_count']

    print(f"Line items collected in step 5: {len(order_lines)}")
    print(f"Line counts reported by the API, summed across orders: {total_line_count_reported}")
    return


@app.cell
def _(order_lines, product_sales):
    #check4: does the total units in product_sales agree with the total quantity in order_lines?

    total_units_from_dict = 0
    for _product in product_sales:
        total_units_from_dict += product_sales[_product]

    total_units_from_lines = 0
    for _line in order_lines:
        total_units_from_lines += _line['quantity']

    print(f"Total units, summed from product_sales: {total_units_from_dict}")
    print(f"Total units, summed directly from order_lines: {total_units_from_lines}")
    return


@app.cell
def _(picked_products, product_sales, top_products):
    #check5: does any product outside the top 5 actually sell more than the 5th-place product?

    _fifth_place_count = top_products[4][1]

    beats_fifth_place = []
    for _product in product_sales:
        if _product not in picked_products and product_sales[_product] > _fifth_place_count:
            beats_fifth_place.append(_product)

    print(f"5th place count: {_fifth_place_count}")
    print(f"Products outside the top 5 that beat this count: {len(beats_fifth_place)}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #7. Working With the Agent

    [#check1 in section 5 step 2 - 3, #check2 - #check5 in section 6]

    I did one sanity check in step 3 (#check1) as explained in section 6, then when we were at step 5, ai suggested doing the planned check right there instead of waiting until step 7 as originally planned. I agreed thus we knew at that point everything was fine. That was #check2.

    But doing that also made me realized doing that as a check point left step 6 - 7 unaudited so I told ai to find a way to check those steps. It suggested #check3, which still did not help audit anything beyond step 5. So I had to tell it to try again and focus on step 6 - 7 which was how I got #check4 and #check5 .

    I kept #check3 anyway as it doesn't really hurt anything.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #8. Reading It Back
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **function 1**

    def get_order_details(order_id):
        _detail_response = requests.get(f"{base_url}/orders/{order_id}")
        _detail = _detail_response.json()
        return _detail['lines']

    **Goes in:** one order_id (a number, like 14298).

    **Comes out:** that order's list of line items (each one a record with product_name, quantity, line_total_dollars, etc.)

    **line asked:** return _detail['lines'] — the function reaches into the order's reply, grabs just the lines list, and hands that back, instead of returning the whole order detail.


    **Function 2**

    def get_orders(from_date, to_date):
        _orders = []
        _first_response = requests.get(f"{base_url}/orders", params={"from_date": str(from_date), "to_date": str(to_date)})
        _first_reply = _first_response.json()
        _total_pages = _first_reply['pagination']['pages']

        for _page in range(1, _total_pages + 1):
            _page_response = requests.get(f"{base_url}/orders", params={"from_date": str(from_date), "to_date": str(to_date), "page": _page})
            _page_reply = _page_response.json()
            for _order in _page_reply['items']:
                _orders.append(_order)

        return _orders, _first_reply['pagination']['total']

    **Goes in:** a start date and an end date (from_date, to_date).

    **Comes out:** two things — the full list of orders in that date range, and the total number the API reports (so you can check they match).

    **line asked:** return _orders, _first_reply['pagination']['total'] — returning two values at once, separated by a comma. Whoever calls this function gets both back together and can unpack them into two separate names, like orders, reported_total = get_orders(...).


    **Change:** days input from 7 to 14

    **Expected outcome:** step 3 and 5b results both increase. as it shows result of 2 weeks instead of one
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **result:**
    collected orders from 32 --> 52
    collected line items 1015 --> 1705

    match. woohoo!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #9. Going Further
    """)
    return


@app.cell
def _(alt, days, orders, pl):
    #going further 1a: revenue by day, as a chart

    revenue_by_day = {}

    for _order in orders:
        _day = _order['order_date'][:10]
        if _day in revenue_by_day:
            revenue_by_day[_day] += _order['order_total_dollars']
        else:
            revenue_by_day[_day] = _order['order_total_dollars']

    _days_list = []
    _revenue_list = []
    for _day in revenue_by_day:
        _days_list.append(_day)
        _revenue_list.append(revenue_by_day[_day])

    revenue_by_day_df = pl.DataFrame({"day": _days_list, "revenue": _revenue_list}).sort("day")

    alt.Chart(revenue_by_day_df).mark_bar().encode(
        x=alt.X("day:O", title="Day"),
        y=alt.Y("revenue:Q", title="Revenue ($)"),
        tooltip=["day", "revenue"]
    ).properties(
        title=f"Revenue by day, last {days} days",
        width=500,
        height=300
    )
    return


@app.cell
def _(orders):
    #investigate: what does our already-collected data show for Oct 22?

    _oct22_orders = []
    for _order in orders:
        if _order['order_date'][:10] == "2026-10-22":
            _oct22_orders.append(_order)

    print(f"Orders on 2026-10-22, from our collected 'orders' list: {len(_oct22_orders)}")
    for _order in _oct22_orders:
        print(f"  order {_order['order_id']}: ${_order['order_total_dollars']:.2f}, placed at {_order['order_date']}")
    return


@app.cell
def _(get_orders):
    #investigate: fetch 22 Oct 2026 fresh from the API, independent of our weekly pull

    _oct22_fetched, _oct22_reported_total = get_orders("2026-10-22", "2026-10-22")

    print(f"Orders on 2026-10-22, freshly fetched: {len(_oct22_fetched)} (API reports total: {_oct22_reported_total})")
    for _order in _oct22_fetched:
        print(f"  order {_order['order_id']}: ${_order['order_total_dollars']:.2f}, placed at {_order['order_date']}")
    return


@app.cell
def _(days, orders):
    #going further 1b: orders and revenue by 2-hour time slot, as a clustered bar chart

    import altair as alt
    import polars as pl

    slot_order_count = {}
    slot_revenue = {}

    for _slot in range(12):
        _label = f"{_slot * 2:02d}-{_slot * 2 + 2:02d}"
        slot_order_count[_label] = 0
        slot_revenue[_label] = 0

    for _order in orders:
        _hour = int(_order['order_date'][11:13])
        _slot = _hour // 2
        _label = f"{_slot * 2:02d}-{_slot * 2 + 2:02d}"
        slot_order_count[_label] += 1
        slot_revenue[_label] += _order['order_total_dollars']

    #orders and revenue are on very different scales (a count vs. dollars),
    #so each is turned into a share of the week's total, which puts them both on a 0-100 scale

    _total_orders = len(orders)
    _total_revenue = 0
    for _order in orders:
        _total_revenue += _order['order_total_dollars']

    _slot_labels = []
    _metric_names = []
    _shares = []

    for _label in slot_order_count:
        _slot_labels.append(_label)
        _metric_names.append("orders")
        _shares.append(slot_order_count[_label] / _total_orders * 100)

    for _label in slot_revenue:
        _slot_labels.append(_label)
        _metric_names.append("revenue")
        _shares.append(slot_revenue[_label] / _total_revenue * 100)

    slot_df = pl.DataFrame({
        "time_slot": _slot_labels,
        "metric": _metric_names,
        "share_percent": _shares
    })

    alt.Chart(slot_df).mark_bar().encode(
        x=alt.X("time_slot:O", title="Time slot (Boston time)", sort=None),
        xOffset="metric:N",
        y=alt.Y("share_percent:Q", title="Share of the week's total (%)"),
        color=alt.Color("metric:N", title="Metric"),
        tooltip=["time_slot", "metric", "share_percent"]
    ).properties(
        title=f"When orders and revenue happen, last {days} days",
        width=600,
        height=350
    )
    return alt, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I first charted revenue by day (going further 1a), just to see which days in the week brought in the most money. The team might need further check on what happened on 22 October as the sale dropped significantly compared to other days. I check both the collected data and the newly fetched from the API. Both numbers agreed at $2743.65 so it is expected to be accurate.

    Then I get curious about what time of day the business operates most actively. So I tried charting both orders and revenue by 2-hour time slot (going further 1b), to see if there's any interesting pattern in when business happens during the day.

    I googled the company name, and this is supposed to be a B2B food business. In that case the spike at midnight (00-02) is a bit weird. What business place orders at midnight? Do their sales person not sleep? They operate globally in different time zones? Or is it their logistics schedule? Or is it just a plot hole, since this is a fictional company anyway?

    This pattern look more like that of a 24-hour convenience store or an online retail platform than a typical B2B food supplier, as it spikes during lunch time, after work, morning, and late-night snack time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #10. Time spent

    5 hours.
    """)
    return


if __name__ == "__main__":
    app.run()
