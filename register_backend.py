import sqlite3
import re
import getpass
from dateutil.relativedelta import relativedelta
import dateutil.parser as parser
from datetime import datetime
from core_backend import *

def check_age(req_age, birthdate):
    dt = datetime.now()
    td = relativedelta(years=-req_age)
    procdate = dt + td
    if not birthdate or birthdate == 0:
        birthdate = input("What is the customer's birthdate? (YYYY-MM-DD) ")
    birthdate = parser.parse(birthdate)
    if birthdate < procdate:
        return ["legal", birthdate]
    else:
        return ["illegal", birthdate]

def search_product(cashier):
    dept = get_result("What kind of item is this: All (1), Produce (2), Meat (3), Deli (4),\nFrozen (5), Grocery (6), Miscellaneous (7)? ", [1, 2, 3, 4, 5, 6, 7])
    if dept == "wrong":
        print("Searching in all departments.")
        dept = 1
    if dept == 1:
        dept = 7
    else:
        dept = dept - 1
    search_type = get_result("Will you be searching by name (1) or by code (2)? ", [1, 2])
    if search_type == 1:
        search = input("Enter the name of the item (Blank for all): ")
    elif search_type == 2:
        search = check_numeric("Enter all of, or a portion of, the item code: ", False, "int")
        search = str(search)
    else:
        return "Invalid search."
    rows = view_mech(search, "stock", search_type)
    inter_rows = []
    if isinstance(rows,list) == False:
        return rows
    if not dept == 7:
        for i in rows:
            if i[14] == dept:
                inter_rows.append(i)    # Only uses entries in the specified department.
        rows = inter_rows
    len_rows = len(rows)
    if len_rows == 1:
        chosen_row = rows[0]
    else:
        seq = 1
        for i in rows:
            print("Number %s: %s" % (seq, i))
            seq = seq + 1
        len_rows = len_rows + 1
        avail_rows = [*range(1, len_rows, 1)]
        selected_row = get_result("Which item would you like to add? ", avail_rows)
        selected_row = selected_row - 1
        chosen_row = rows[selected_row]
        final_data = process_item(chosen_row, cashier)
    return final_data

def process_item(item_data, cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    pname = item_data[1]        # I figured it's better for readability, and my own comprehension,
    weigh = item_data[3]        # to use all these variable names rather than repeatedly referencing
    available = item_data[4]    # final_row over and over.
    spec_quant = item_data[7]
    price = item_data[8]
    tax = item_data[9]
    ebt = item_data[10]
    re_points = item_data[11]
    age = item_data[12]
    disc_price = item_data[13]
    if age > 0:
        try:
            cur.execute("SELECT cust_age FROM current_trans_meta WHERE cashier = ?", (cashier,))
            cust_age = cur.fetchone()
            cust_age = cust_age[0]
        except TypeError:
            cust_age = 0
        age_req = check_age(age, cust_age)
        legal = age_req[0]
        cust_date = age_req[1]
        if cust_age != cust_date:
            cur.execute("UPDATE current_trans_meta SET cust_age = ? WHERE cashier = ?", (cust_date,cashier))
        if legal == "illegal":
            return "Not for sale"
    if spec_quant:
        if weigh:
            numtype = "float"
        else:
            numtype = "int"
        user_weight = check_numeric("How many/much of this item is being purchased? ", False, numtype)
        if not isinstance(user_weight, str): 
            if user_weight > available:
                return "Cannot sell more  than {}.".format(available)
            if user_weight > 20:
                should_enter = get_true("This is a large quantity of items. Are you sure of this? (Default is no)", 0)
                if should_enter == 0:
                    return "Not selling item."
        else:
            return "Please enter a number."
    else:
        user_weight = 1
    price_delta = 0
    try:
        cur.execute("SELECT disc_card FROM current_trans_meta WHERE cashier = ?", (cashier,))
        is_disc = cur.fetchone()
        is_disc = is_disc[0]
        if is_disc:
            price_delta = price - disc_price
    except TypeError:
        is_disc = 0
        price_delta = 0
    final_price = (price - price_delta) * user_weight
    final_price = round(final_price,2)
    if tax:
        cur.execute("SELECT sales_tax FROM store_data WHERE store_id = 1")
        sales_tax = cur.fetchone()
        sales_tax = sales_tax[0]
        product_tax = sales_tax * final_price
    else:
        product_tax = 0
    if ebt:
        ebt_price = final_price
    else:
        ebt_price = 0
    if re_points:
        points = final_price
    cur.execute("INSERT INTO current_trans VALUES (NULL,?,?,?,?,?,?,?,?)", (pname, user_weight, price, final_price, product_tax, ebt_price, points, price_delta))
    conn.commit()
    conn.close()
    return "Added %s" % pname

def locate_product_by_code():
    conn = sqlite3.connect("store.db")      # This needs its own function since
    cur = conn.cursor()                     # view_mech returns several results in a list.
    search = input("Enter the item code: ")
    cur.execute("SELECT * FROM stock WHERE code = ?", (search,))
    result = cur.fetchone()
    if not result:
        return "Item not found."
    else:
        return result