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
    department TEXT
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