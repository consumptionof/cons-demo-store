import sqlite3

conn = sqlite3.connect("store.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS stock (
    id1 INTEGER PRIMARY KEY,
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
    disc_price REAL
    )
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS coupons (
    id2 INTEGER PRIMARY KEY,
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
    id3 INTEGER PRIMARY KEY,
    fname TEXT,
    lname TEXT,
    phone INTEGER,
    id INTEGER,
    points INTEGER
)
""")

conn.commit()
conn.close()