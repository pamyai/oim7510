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
    1. The Question

    The operations manager would use this tool to understand what happened in the business over the past week. It gives a quick view of sales, popular products, and any orders that still need attention.

    The tool helps the manager decide whether sales are performing well, which products are driving demand, and whether there are unshipped orders that need follow-up.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    2 - My Plan Before AI
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


if __name__ == "__main__":
    app.run()
