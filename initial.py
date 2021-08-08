from sqlite3.dbapi2 import SQLITE_DROP_VIEW
from core_backend import stop_dupe
from inventory_backend import check_numeric
import sqlite3

conn = sqlite3.connect("store.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY,
    name TEXT,
    code INT,
    weigh INTEGER,
    quan REAL,
    low_quan REAL,
    restock INTEGER,
    spec_quant INTEGER,
    price REAL,
    tax INTEGER,
    ebt INTEGER,
    re_points INTEGER,
    age INTEGER,
    disc_price REAL,
    department INTEGER
    )
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS coupons (
    id INTEGER PRIMARY KEY,
    name TEXT,
    code INTEGER,
    item_code INTEGER,
    each_weigh INTEGER,
    value REAL,
    min REAL,
    max REAL,
    doubled INT,
    disc_card INT,
    expire TEXT,
    re_cost INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,
    fname TEXT,
    lname TEXT,
    phone INTEGER,
    code INTEGER,
    points INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS employees(
    id INTEGER PRIMARY KEY,
    fname TEXT,
    lname TEXT,
    actype INTEGER,
    login INTEGER,
    passcode INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS store_data(
    store_id INTEGER PRIMARY KEY,
    name TEXT,
    sales_tax REAL
)
""")

store_name = input("What is the name of the store? ")
sales_tax = "not_numeric"
while isinstance(sales_tax, str):
    sales_tax = check_numeric("What is the sales tax (expressed as a decimal, like 0.08)? ", False, "float")
cur.execute("INSERT INTO store_data VALUES (NULL,?,?)", (store_name, sales_tax))

is_login_numeric = 0
is_passcode_numeric = 0
fname = input("What is the initial manager's name? ")
lname = input("What is the manager's last name? ")
while is_login_numeric == 0:
    login = check_numeric("What is the manager's login code? ", False, "int")
    if login == "not_numeric":
        print("Error: Please enter an integer. This account is required.")
    else:
        is_login_numeric = 1
while is_passcode_numeric == 0:
    passcode = check_numeric("What is the manager's passcode? ", False, "int")
    if passcode == "not_numeric":
        print("Error: Please enter an integer. This account is required.")
    else:
        is_passcode_numeric = 1
cur.execute("INSERT INTO employees VALUES (NULL,?,?,2,?,?)", (fname, lname, login, passcode))

conn.commit()
conn.close()

print("Welcome to the store, {}.".format(fname))