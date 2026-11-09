"""Write one CSV file per table of the Babson Bean Café database into projects/db/data/.

Run it from the root folder of the repository:
    uv run python projects/db/make_data.py

The random seed is fixed, so it writes the same files every time.
"""
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

random.seed(7510)

AS_OF = date(2026, 11, 7)              # the as_of date Part B counts back from
START = AS_OF - timedelta(days=364)    # 12 months up to as_of, both days included
PRICE_CHANGE = date(2026, 7, 1)        # coffee prices went up 25 cents on this day
DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)


def money(cents):
    """Money is kept in whole cents while generating, and written as dollars."""
    return f"{cents / 100:.2f}"


def write(name, header, rows):
    with open(DATA / f"{name}.csv", "w", newline="") as _f:
        _w = csv.writer(_f)
        _w.writerow(header)
        _w.writerows(rows)
    print(f"{name}.csv: {len(rows)} rows")


# ---------------------------------------------------------------- members
FIRST_NAMES = [
    "Aisha", "Ben", "Carla", "Dev", "Emma", "Felipe", "Grace", "Hiro", "Isla", "Jamal",
    "Kate", "Liam", "Maya", "Noah", "Olivia", "Priya", "Quinn", "Rosa", "Sam", "Tara",
    "Uma", "Victor", "Wen", "Xavier", "Yara", "Zoe", "Arjun", "Bea", "Chen", "Dana",
    "Eli", "Fatima", "Gabe", "Hana", "Ivan", "Jade", "Kofi", "Lena", "Mateo", "Nina",
    "Omar", "Pam", "Ravi", "Sofia", "Theo", "Emma", "Leo", "Mia", "Sam", "Ana",
]  # two Emmas and two Sams on purpose: first names are not unique
NEVER_ORDER = {46, 47, 48, 49, 50}     # members who joined and never ordered

members = []
for _i, _name in enumerate(FIRST_NAMES, start=1):
    if _i in (49, 50):                 # two signed up in the last three weeks
        _join = AS_OF - timedelta(days=random.randint(1, 20))
    else:
        _join = START - timedelta(days=365) + timedelta(days=random.randint(0, 690))
    _mobile = f"617-555-{1000 + _i * 37:04d}"
    _email = f"{_name.lower()}{_i}@babson.edu" if random.random() < 0.7 else ""
    members.append({
        "id": _i, "name": _name, "mobile": _mobile, "email": _email,
        "join": _join, "points": random.randint(0, 250),
    })

# ---------------------------------------------------------------- menu
# (name, category, current price in cents, cost in cents, available today)
MENU = [
    ("Espresso", "coffee", 300, 60, True),
    ("Americano", "coffee", 350, 70, True),
    ("Latte", "coffee", 475, 110, True),
    ("Cappuccino", "coffee", 450, 105, True),
    ("Flat White", "coffee", 475, 110, True),
    ("Mocha", "coffee", 525, 140, True),
    ("Cold Brew", "coffee", 450, 90, True),
    ("Iced Latte", "coffee", 500, 120, True),
    ("Pumpkin Spice Latte", "coffee", 575, 150, False),  # seasonal, off the menu now
    ("Chai Latte", "tea", 475, 115, True),
    ("Matcha Latte", "tea", 525, 150, True),
    ("Earl Grey", "tea", 300, 50, True),
    ("Green Tea", "tea", 300, 50, True),
    ("Thai Iced Tea", "tea", 450, 100, True),
    ("Butter Croissant", "food", 375, 120, True),
    ("Blueberry Muffin", "food", 350, 110, True),
    ("Bagel with Cream Cheese", "food", 400, 130, True),
    ("Avocado Toast", "food", 750, 290, True),
    ("Ginger Scone", "food", 375, 115, True),   # on the menu, but stopped selling
    ("Chocolate Chip Cookie", "food", 250, 70, True),
    ("Bottled Water", "other", 200, 60, True),
    ("Sparkling Water", "other", 275, 90, True),
    ("Orange Juice", "other", 400, 160, True),
]
POPULARITY = [6, 8, 14, 9, 7, 5, 8, 9, 6, 7, 6, 3, 3, 4, 8, 6, 5, 3, 3, 6, 4, 2, 3]
SCONE_LAST_SALE = AS_OF - timedelta(days=75)

menu = [
    {"id": _i, "name": _n, "cat": _c, "price": _p, "cost": _k, "avail": _a}
    for _i, (_n, _c, _p, _k, _a) in enumerate(MENU, start=1)
]


def on_sale(product, day):
    if product["name"] == "Pumpkin Spice Latte":
        return day <= date(2025, 12, 31)
    if product["name"] == "Ginger Scone":
        return day <= SCONE_LAST_SALE
    return True


def price_on(product, day):
    """The price charged on that day: coffee was 25 cents cheaper before PRICE_CHANGE."""
    if product["cat"] == "coffee" and day < PRICE_CHANGE:
        return product["price"] - 25
    return product["price"]


# ---------------------------------------------------------------- options
OPTIONS = [
    ("Extra Shot", 100, 25), ("Oat Milk", 75, 30), ("Almond Milk", 75, 30),
    ("Vanilla Syrup", 50, 10), ("Caramel Syrup", 50, 10), ("Hazelnut Syrup", 50, 10),
    ("Whipped Cream", 50, 15), ("Extra Hot", 0, 0), ("Light Ice", 0, 0),
]
options = [
    {"id": _i, "name": _n, "price": _p, "cost": _k}
    for _i, (_n, _p, _k) in enumerate(OPTIONS, start=1)
]

# ---------------------------------------------------------------- orders
# A campus café: busy on weekdays, quiet on weekends, winter break and summer.
days = [START + timedelta(days=_d) for _d in range(365)]


def day_weight(day):
    _w = 1.0
    if day.weekday() == 5:
        _w = 0.35
    elif day.weekday() == 6:
        _w = 0.25
    if date(2025, 12, 20) <= day <= date(2026, 1, 18):
        _w *= 0.3
    if date(2026, 5, 20) <= day <= date(2026, 8, 25):
        _w *= 0.4
    return _w


HOURS = list(range(7, 19))                       # open 7:00 to 18:59
HOUR_WEIGHTS = [6, 10, 9, 6, 5, 8, 7, 4, 4, 5, 3, 2]

order_days = sorted(random.choices(days, weights=[day_weight(_d) for _d in days], k=1200))
order_times = sorted(
    datetime(_d.year, _d.month, _d.day,
             random.choices(HOURS, weights=HOUR_WEIGHTS)[0], random.randint(0, 59))
    for _d in order_days
)

orders, lines, line_options, payments_by_order = [], [], [], {}
line_id = 0
for _order_id, _when in enumerate(order_times, start=1):
    _day = _when.date()
    _channel = "app" if random.random() < 0.3 else "counter"

    # member or not; a member only orders on or after the day they joined
    _member = None
    if random.random() < (0.55 if _channel == "app" else 0.35):
        _eligible = [_m for _m in members
                     if _m["join"] <= _day and _m["id"] not in NEVER_ORDER]
        if _eligible:
            _member = random.choice(_eligible)
    orders.append({"id": _order_id, "member": _member, "when": _when, "channel": _channel})

    # lines, and options on the drinks
    _total = 0
    _for_sale = [_p for _p in menu if on_sale(_p, _day)]
    _weights = [POPULARITY[_p["id"] - 1] for _p in _for_sale]
    for _ in range(random.choices([1, 2, 3], weights=[60, 30, 10])[0]):
        line_id += 1
        _product = random.choices(_for_sale, weights=_weights)[0]
        _qty = random.choices([1, 2, 3], weights=[80, 17, 3])[0]
        _price = price_on(_product, _day)
        lines.append({"id": line_id, "order": _order_id, "prod": _product["id"],
                      "qty": _qty, "price": _price})
        _unit = _price
        if _product["cat"] in ("coffee", "tea"):
            _n_options = random.choices([0, 1, 2], weights=[50, 35, 15])[0]
            for _option in random.sample(options, _n_options):   # no option twice on a line
                line_options.append({"line": line_id, "option": _option["id"],
                                     "price": _option["price"]})
                _unit += _option["price"]
        _total += _qty * _unit                  # options are charged once per unit

    # payments: add up to the total; only members can pay with points
    _main_method = "app" if _channel == "app" else random.choices(["card", "cash"], [70, 30])[0]
    _pays = []
    if _member and random.random() < 0.2:
        _points = min(_total, random.choice([100, 200, 300, 500]))
        _pays.append(["points", _points])
        if _total - _points > 0:
            _pays.append([_main_method, _total - _points])
    else:
        _pays.append([_main_method, _total])
    payments_by_order[_order_id] = {"total": _total, "pays": _pays}

# ---------------------------------------------------------------- the rule broken on purpose
# "An order's payments add up to the order's total" -- broken in exactly two orders.
_candidates = [_o for _o, _p in payments_by_order.items()
               if _p["total"] >= 300 and len(_p["pays"]) == 1]
broken_short, broken_over = random.sample(_candidates, 2)
payments_by_order[broken_short]["pays"][0][1] -= 100          # paid $1.00 too little
payments_by_order[broken_over]["pays"].append(["card", 150])  # paid $1.50 too much

payments = []
for _order_id in sorted(payments_by_order):
    for _method, _amount in payments_by_order[_order_id]["pays"]:
        payments.append({"id": len(payments) + 1, "order": _order_id,
                         "method": _method, "amount": _amount})

# ---------------------------------------------------------------- check the other rules
assert all(_p["price"] >= _p["cost"] for _p in menu)
assert all(_l["qty"] > 0 for _l in lines)
assert all(_p["amount"] > 0 for _p in payments)
assert all(_p["method"] in ("cash", "card", "app", "points") for _p in payments)
assert len({(_lo["line"], _lo["option"]) for _lo in line_options}) == len(line_options)
assert all(_o["member"] is None or _o["member"]["join"] <= _o["when"].date() for _o in orders)
for _o in orders:
    if _o["member"] is None:
        assert all(_m != "points" for _m, _ in payments_by_order[_o["id"]]["pays"])

# ---------------------------------------------------------------- write the files
write("member",
      ["member_id", "member_name", "member_mobile", "member_email", "member_join_date", "member_points"],
      [[_m["id"], _m["name"], _m["mobile"], _m["email"], _m["join"], _m["points"]] for _m in members])
write("menu",
      ["prod_id", "prod_name", "prod_cat", "prod_price", "prod_cost", "prod_avail"],
      [[_p["id"], _p["name"], _p["cat"], money(_p["price"]), money(_p["cost"]),
        "true" if _p["avail"] else "false"] for _p in menu])
write("options",
      ["option_id", "option_name", "option_price", "option_cost"],
      [[_o["id"], _o["name"], money(_o["price"]), money(_o["cost"])] for _o in options])
write("orders",
      ["order_id", "member_id", "order_datetime", "order_channel"],
      [[_o["id"], _o["member"]["id"] if _o["member"] else "",
        _o["when"].strftime("%Y-%m-%d %H:%M:%S"), _o["channel"]] for _o in orders])
write("order_line",
      ["line_id", "order_id", "prod_id", "line_qty", "line_price"],
      [[_l["id"], _l["order"], _l["prod"], _l["qty"], money(_l["price"])] for _l in lines])
write("line_option",
      ["line_id", "option_id", "option_price_charged"],
      [[_lo["line"], _lo["option"], money(_lo["price"])] for _lo in line_options])
write("payment",
      ["payment_id", "order_id", "payment_method", "payment_amt"],
      [[_p["id"], _p["order"], _p["method"], money(_p["amount"])] for _p in payments])

# ---------------------------------------------------------------- what to write down
print()
print(f"as_of date: {AS_OF}, data from {START}")
print(f"Rule broken on purpose (payments = order total), in exactly two orders:")
print(f"  order {broken_short}: total {money(payments_by_order[broken_short]['total'])}, paid $1.00 too little")
print(f"  order {broken_over}: total {money(payments_by_order[broken_over]['total'])}, paid $1.50 too much")
_ordered = {_o["member"]["id"] for _o in orders if _o["member"]}
print(f"Members who never ordered: {sorted(_m['id'] for _m in members if _m['id'] not in _ordered)}")
print(f"Orders with no member: {sum(1 for _o in orders if _o['member'] is None)}")
