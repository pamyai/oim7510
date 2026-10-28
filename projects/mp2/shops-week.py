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
def _(base_url, from_date, to_date):
    #step2: request orders in the date range

    import requests

    response = requests.get(f"{base_url}/orders", params={"from_date": str(from_date), "to_date": str(to_date)})
    reply = response.json()

    print(f"This page has {len(reply['items'])} orders")
    print(f"Total orders in the date range: {reply['pagination']['total']}")
    return reply, requests


@app.cell
def _(base_url, from_date, reply, requests, to_date):
    #step3: collect every page of orders

    orders = []
    total_pages = reply['pagination']['pages']

    for page in range(1, total_pages + 1):
        page_response = requests.get(f"{base_url}/orders", params={"from_date": str(from_date), "to_date": str(to_date), "page": page})
        page_reply = page_response.json()
        for _order in page_reply['items']:
            orders.append(_order)
    #check1
    print(f"Collected {len(orders)} orders out of {reply['pagination']['total']} reported")
    return (orders,)


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
def _(base_url, orders, requests):
    #step5: get line items for each order

    order_lines = []

    for _order in orders:
        _detail_response = requests.get(f"{base_url}/orders/{_order['order_id']}")
        _detail = _detail_response.json()
        for _line in _detail['lines']:
            order_lines.append(_line)

    print(f"Collected {len(order_lines)} line items from {len(orders)} orders")
    return (order_lines,)


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

    I checked four things a second way, all shown in the cells below:

    **1. Did I collect every order?**
    In step 3, the API's pagination said there were 35 orders total in this date range. I collected orders page by page and counted 35 orders in my `orders` list. 35 equals 35, so I have every order, not just the first page.

    **2. Does each order's line-item total agree with its reported order total?**
    An order's `order_total_dollars` (from `/shop/orders`) should equal the sum of its `line_total_dollars` values (from `/shop/orders/{order_id}`), since the order total is just all its lines added up. I checked this for all 35 orders: I summed each order's lines separately and compared that sum to the order's reported total, allowing a one-cent gap for rounding. 0 of 35 orders disagreed, so the revenue and line-item numbers in this report agree with each other.

    **3. Did I collect every line item?**
    Each order in `/shop/orders` already reports its own `line_count`, a count of how many line items it has. I summed `line_count` across all 35 orders and compared it to the number of line items I actually collected in step 5. Both came to 1065, so step 6 and step 7, which depend on having every line item, are built on a complete set.

    **4. Does the units-sold total in `product_sales` agree with the raw line items?**
    I summed the units two different ways: once by adding up every value already stored in the `product_sales` dictionary (built in step 6), and once by going back to `order_lines` directly and adding up every `quantity` field. Both came to 25,671 units, so building the dictionary did not drop or double-count anything.

    **5. Are the top 5 products really the top 5?**
    The picking method in step 7 works by repeatedly scanning for the highest remaining count, so it should be correct by construction, but I checked it a different way anyway: I took the 5th-place product's count (446 units) and scanned every other product not in the top 5 to see if any of them actually sold more. None did, which confirms the top 5 list is right.
    """)
    return


@app.cell
def _(base_url, orders, requests):
    #check2: does the sum of an order's lines agree with its order_total_dollars?

    mismatch_count = 0

    for _order in orders:
        _detail_response = requests.get(f"{base_url}/orders/{_order['order_id']}")
        _detail = _detail_response.json()

        _line_sum = 0
        for _line in _detail['lines']:
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

    I did one sanity check in step 3 as explained in section 6, then when we were at step 5, ai suggested doing the planned check right there instead of waiting until step 7 as originally planned. I agreed thus we knew at that point everything was fine. That was check #2.

    But doing that also made me realized doing that as a check point left step 6 - 7 unaudited so I told ai to find a way to check those steps. It suggested check #3, which still did not help audit anything beyond step 5. So I had to tell it to try again and focus on step 6 - 7 which was how I got check #4 - 5. I kept check #3 anyway as it doesn't really hurt anything.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
