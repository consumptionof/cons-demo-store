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
    if birthdate == 0 or birthdate == "0":
        birthdate = input("What is the customer's birthdate? (YYYY-MM-DD) ")
    birthdate = parser.parse(birthdate)
    if birthdate < procdate:
        return ["legal", birthdate]
    else:
        return ["illegal", birthdate]

def search_product(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
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
    search = "%"+search+"%"
    if search_type == 1:
        cur.execute("SELECT * FROM stock WHERE name LIKE ? COLLATE NOCASE", (search,))
    else:
        cur.execute("SELECT * FROM stock WHERE code LIKE ?", (search,))
    rows = cur.fetchall()
    inter_rows = []
    if not isinstance(rows,list):
        search = re.sub("%","",search)
        return "No results for %s." % search
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
    pname = item_data[1]        
    item_code = item_data[2]    # I figured it's better for readability, and my own comprehension,
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
    final_price_delta = price_delta * user_weight
    final_price = (price * user_weight) - final_price_delta
    final_price = round(final_price,2)
    if tax:
        cur.execute("SELECT sales_tax FROM store_data WHERE store_id = 1")
        sales_tax = cur.fetchone()
        sales_tax = sales_tax[0]
        product_tax = sales_tax * final_price
        product_tax = round(product_tax,2)
    else:
        product_tax = 0
    if ebt:
        ebt_price = final_price
    else:
        ebt_price = 0
    if re_points:
        points = final_price
    else:
        points = 0
    cur.execute("INSERT INTO current_trans VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)",
    (pname, item_code, user_weight, price, final_price, product_tax, ebt_price, points, final_price_delta, 0, item_code))
    conn.commit()
    conn.close()
    return "Added %s" % pname

def search_coupon(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    coupon_type = get_result("Do you want to search for a coupon name (1) or a code affected by the coupon (2)? ", [1, 2])
    if coupon_type == 1:
        search = input("Enter (a part of) the coupon's name (Blank for all): ")
        search = "%"+search+"%"
        cur.execute("SELECT * FROM coupons WHERE name LIKE ? COLLATE NOCASE", (search,))
    elif coupon_type == 2:
        search = input("Enter (a part of) the affected item's code (Blank for all): ")
        search = "%"+search+"%"
        cur.execute("SELECT * FROM coupons WHERE item_code LIKE ?", (search,))
    rows = cur.fetchall()
    inter_rows = []
    if isinstance(rows,list) == False:
        return rows
    dt = datetime.now()
    for i in rows:
        expire = i[10]
        try:
            expire = int(expire)        # Is expire 0? For some reason, this is
            inter_rows.append(i)        # the first method for finding this that's worked.
        except ValueError:              # If not, then it's an expiration date.
            coupon_date = datetime.fromisoformat(expire)
            if coupon_date > dt:
                inter_rows.append(i)    # Only uses entries that haven't expired.
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
        selected_row = get_result("Which coupon would you like to add? ", avail_rows)
        selected_row = selected_row - 1
        chosen_row = rows[selected_row]
    final_data = process_coupon(chosen_row, cashier)
    return final_data

def process_coupon(coupon_data, cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    coupon_name = coupon_data[1]
    coupon_code = coupon_data[2]
    affected_code = coupon_data[3]
    coupon_type = coupon_data[4]
    coupon_discount = coupon_data[5]
    minimum = coupon_data[6] 
    max_apps = coupon_data[7]
    doubled = coupon_data[8]
    disc_card = coupon_data[9]
    expire = coupon_data[10]
    point_cost = coupon_data[11]
    cur.execute("SELECT * FROM current_trans WHERE icode = ?", (affected_code,))
    matches = cur.fetchall()
    if not matches:
        return "Coupon must match previous sale."
    dt = datetime.now()             # I only recently realized that the
    try:                            # search by code function doesn't check expirations.
        expire = int(expire)        # Is expire 0?
    except ValueError:              # If not, then it's an expiration date.
        coupon_date = datetime.fromisoformat(expire)
        if coupon_date < dt:
            return "This coupon is expired."
    if disc_card:
        cur.execute("SELECT disc_card FROM current_trans_meta WHERE cashier = ?", (cashier,))
        is_card = cur.fetchone()
        is_card = is_card[0]
        is_card = int(is_card)
        if not is_card:
            return "This coupon requires a rewards card."
    if point_cost:
        cur.execute("SELECT points FROM cards WHERE phone = ?", (is_card,))
        available_points = cur.fetchone()
        available_points = available_points[0]
        if point_cost > available_points:
            return "Not enough points for this coupon."
    total_items = 0
    total_price = 0
    total_ebt = 0
    total_rewards = 0
    total_tax = 0
    match_count = len(matches)
    for i in range(0, match_count):                 # Adds up all the instances of an item, and then
        prov_list = matches[i]                      # adds one coupon with each total.
        total_items = total_items + prov_list[3]    # Turns out you can't just do "for i in matches"
        total_price = total_price + prov_list[5]    # # because it's a list of tuples. Who would have guessed?
        total_tax = total_tax + prov_list[6]
        total_ebt = total_ebt + prov_list[7]
        total_rewards = total_rewards + prov_list[8]
    if total_items < minimum:
        return "Not enough items for coupon."
    if max_apps and total_items >= max_apps:
        total_apps = max_apps
    else:
        total_apps = total_items
    if coupon_type == 1:
        price_delta = -(coupon_discount * total_apps)
    elif coupon_type == 2:
        price_delta = -(total_price * coupon_discount)
    else:
        interim = coupon_discount * total_items
        price_delta = interim - total_price
    price_delta = round(price_delta,2)
    if total_tax:
        cur.execute("SELECT sales_tax FROM store_data WHERE store_id = 1")
        tax_discount = cur.fetchone()
        tax_discount = tax_discount[0]
        tax_discount = (tax_discount * price_delta)
        tax_discount = round(tax_discount,2)
    else:
        tax_discount = 0
    if total_rewards:
        coupon_rewards = price_delta
    else:
        coupon_rewards = 0
    cur.execute("INSERT INTO current_trans VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)",
    (coupon_name, affected_code, total_apps, coupon_discount, price_delta,
    tax_discount, total_ebt, coupon_rewards, price_delta, point_cost, coupon_code))
    if doubled:
        cur.execute("INSERT INTO current_trans VALUES (NULL,?,?,?,?,?,?,?,?,?,?)",
        ("Doubled coupon", affected_code, total_apps, coupon_discount, price_delta,
        tax_discount, total_ebt, total_rewards, price_delta, point_cost, coupon_code))
    conn.commit()
    conn.close()
    return "Added coupon: %s" % coupon_name

def process_card(customer, cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    fname = customer[1]
    lname = customer[2]
    phone = customer[3]
    cust_code = customer[5]
    cur.execute("SELECT disc_card FROM current_trans_meta WHERE cashier = ?", (cashier,))
    old_phone = cur.fetchone()
    if old_phone:
        cur.execute("SELECT points FROM cards WHERE code = ?", (cust_code,))
        cust_points = cur.fetchone()
        try:
            cust_points = cust_points[0]
        except TypeError:
            cust_points = 0
        cur.execute("SELECT req_points FROM current_trans")
        trans_points = cur.fetchall()
        num_of_items = len(trans_points)
        total_points = 0
        for i in range(0, num_of_items):
            prov_points = trans_points[i]
            prov_points = prov_points[0]
            total_points = total_points + prov_points
        if total_points > cust_points:
            print("Insufficient points for coupons. Removing points coupons.")
            cur.execute("DELETE FROM current_trans WHERE req_points > 0")
    cur.execute("UPDATE current_trans_meta SET disc_card = ? WHERE cashier = ?", (phone, cashier))
    conn.commit()
    conn.close()
    return "Welcome %s %s to the store." % (fname, lname)

def search_card_by_phone(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    phone = input("What is the customer's phone number? (Blank to view all) ")
    phone = str(phone)      # You can never be too sure.
    phone = "%"+phone+"%"
    cur.execute("SELECT * FROM cards WHERE phone LIKE ?", (phone,))
    rows = cur.fetchall()
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
        selected_row = get_result("Which account would you like to add? ", avail_rows)
        selected_row = selected_row - 1
        chosen_row = rows[selected_row]
    final_data = process_card(chosen_row, cashier)
    return final_data

def locate_by_code(cashier):
    conn = sqlite3.connect("store.db")      # Know the code of an item and don't
    cur = conn.cursor()                     # want to jump through too many hoops?
    search = input("Enter the code: ")      # This function is for you.
    queries = ["SELECT * FROM stock WHERE code = ?",
    "SELECT * FROM coupons WHERE code = ?",
    "SELECT * FROM cards WHERE code = ?"]
    for i in range(0, 3):
        cur.execute(queries[i], (search,))
        result = cur.fetchone()
        if result and i == 0:
            finality = process_item(result,cashier)     # Maybe not the most elegant way of doing it,
            break                                       # but it beats a bunch of nested if statements.
        if result and i == 1:
            finality = process_coupon(result,cashier)
            break
        if result and i == 2:
            finality = process_card(result,cashier)
            break
    if not result:
        finality = "Item not found."
    return finality

def void():
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    entry_type = get_result("Would you like to search by name (1) or by code (2)? ", [1, 2])
    if entry_type == 1:
        del_item = input("What istthe name of the item? ")
        del_item = "%"+del_item+"%"
        cur.execute("SELECT * FROM current_trans WHERE pname LIKE ? COLLATE NOCASE", (del_item,))
    elif entry_type == 2:
        del_item = check_numeric("What is the item code? ", False, "int")
        del_item = str(del_item)
        del_item = "%"+del_item+"%"
        cur.execute("SELECT * FROM current_trans WHERE icode LIKE ?", (del_item,))
    rows = cur.fetchall()
    if not isinstance(rows,list):
        del_item = re.sub("%","",del_item)
        return "No results found for %s." % del_item
    len_rows = len(rows)
    coupon_entries = []
    if len_rows == 1:
        chosen_row = rows[0]
    else:
        seq = 1
        for i in rows:
            print("Number %s: %s" % (seq, i))
            if i[2] != i[11]:
                coupon_entries.append(i)
            seq = seq + 1
        len_rows = len_rows + 1
        avail_rows = [*range(1, len_rows, 1)]
        selected_row = get_result("Which item would you like to remove? ", avail_rows)
        selected_row = selected_row - 1
        chosen_row = rows[selected_row]
    chosen_row_id = chosen_row[0]
    cur.execute("DELETE FROM current_trans WHERE id = ?", (chosen_row_id,))
    print("Deleted entry: {}".format(chosen_row))
    if len(coupon_entries) > 0:
        print("Deleting all coupons related to this item.")
        for i in coupon_entries:
            coupon_entry_id = i[0]
            cur.execute("DELETE FROM current_trans WHERE id = ?", (coupon_entry_id,))
    conn.commit()
    conn.close()
    return "Successfully deleted entry."

def void_last():
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("SELECT pname FROM current_trans WHERE id = (SELECT MAX(id) FROM current_trans)")
    pname = cur.fetchone()
    pname = pname[0]
    cur.execute("DELETE FROM current_trans WHERE id = (SELECT MAX(id) FROM current_trans)")
    conn.commit()
    conn.close()
    return "Deleted last {} from the transaction".format(pname)