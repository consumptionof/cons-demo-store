import sqlite3
import re
import math
from dateutil.relativedelta import relativedelta
import dateutil.parser as parser
from datetime import datetime
from core_backend import *
import os

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
    dept = get_result("What kind of item is this: All (1), Produce (2), Meat (3), Deli (4),\nDairy (5), Frozen (6), Grocery (7), Miscellaneous (8)? ", [1, 2, 3, 4, 5, 6, 7, 8])
    if dept == "wrong":
        print("Searching in all departments.")
        dept = 1
    if dept == 1:
        dept = 8
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
    search = sanitize(search)
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
    if dept != 8:
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
        if cust_age != cust_date and legal == "legal":
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
                return "Cannot sell more than {}.".format(available)
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
    final_price = (price * user_weight)# - final_price_delta
    final_price = round(final_price,2)
    if tax:
        cur.execute("SELECT sales_tax FROM store_data WHERE store_id = 1")
        sales_tax = cur.fetchone()
        sales_tax = sales_tax[0]
        product_tax = sales_tax * final_price
        product_tax = round(product_tax,2)
    else:
        product_tax = 0
    if re_points:
        points = final_price
    else:
        points = 0
    cur.execute("INSERT INTO current_trans_{} VALUES (NULL,'{}',{},{},{},{},{},{},{},{},{},{})".format(
    cashier, pname, item_code, user_weight, price, final_price, product_tax, ebt, points, 0, 0, item_code))
    if final_price_delta > 0 and is_disc > 0:
        listed_delta = abs(final_price_delta)
        price_delta = -price_delta
        final_price_delta = -final_price_delta
        disc_points = final_price_delta
        cur.execute("INSERT INTO current_trans_{} VALUES (NULL,'{}',{},{},{},{},{},{},{},{},{},{})".format(
        cashier, pname, item_code, user_weight, price_delta, final_price_delta, 0, ebt, disc_points, listed_delta, 0, 1))
    cur.execute("UPDATE stock SET quan = quan - ? WHERE code = ?", (user_weight, item_code))
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
    cur.execute("SELECT * FROM current_trans_{} WHERE icode = {}".format(cashier, affected_code,))
    matches = cur.fetchall()
    if not matches:
        return "Coupon must match previous sale."
    if max_apps > 0:
        cur.execute("SELECT user_weight FROM current_trans_{} WHERE coupon_code = {}".format(cashier, coupon_code))
        apps_in_trans = cur.fetchall()
        if apps_in_trans:
            number_of_apps = 0
            for i in apps_in_trans:
                number_of_apps += i[0]
            if number_of_apps >= max_apps:
                return "This coupon cannot be applied any further."
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
    cur.execute("INSERT INTO current_trans_{} VALUES (NULL,'{}',{},{},{},{},{},{},{},{},{},{})".format(
    cashier, coupon_name, affected_code, total_apps, coupon_discount, price_delta,
    tax_discount, total_ebt, coupon_rewards, price_delta, point_cost, coupon_code))
    if doubled:
        cur.execute("INSERT INTO current_trans_{} VALUES (NULL,'{}',{},{},{},{},{},{},{},{},{},{})".format(
        "Doubled coupon", affected_code, total_apps, coupon_discount, price_delta,
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
    old_phone = old_phone[0]
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
            cur.execute("DELETE FROM current_trans_{} WHERE req_points > 0".format(cashier))
    else:
        pass
        cur.execute("SELECT id, icode FROM current_trans_{}".format(cashier))
        product_codes = cur.fetchall()
        for i in product_codes:
            entry = i[0]
            icode = i[1]
            cur.execute("SELECT price, disc_price FROM stock WHERE code = ?", (icode,))
            price_disc = cur.fetchone()
            normal_price = price_disc[0]
            disc_price = price_disc[1]
            if normal_price != disc_price:
                cur.execute("SELECT pname, icode, user_weight, final_price, paid_ebt FROM current_trans_{} WHERE id = {}".format(cashier, entry) )
                deets = cur.fetchone()
                pname = deets[0]
                item_code = deets[1]
                weight = deets[2]
                current_price = deets[3]
                ebt = deets[4]
                price_delta = disc_price - normal_price
                price_weight = disc_price * weight
                final_price_delta = price_weight - current_price
                disc_points = final_price_delta
                listed_delta = final_price_delta
                cur.execute("INSERT INTO current_trans_{} VALUES (NULL,'{}',{},{},{},{},{},{},{},{},{},{})".format(
                cashier, pname, item_code, weight, price_delta, final_price_delta, 0, ebt, disc_points, listed_delta, 0, 1))
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
        selected_row = get_result("Which account would you like to use? ", avail_rows)
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
        if result and i == 1:                           # I think.
            finality = process_coupon(result,cashier)
            break
        if result and i == 2:
            finality = process_card(result,cashier)
            break
    if not result:
        finality = "Item not found."
    return finality

def void(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    entry_type = get_result("Would you like to search by name (1) or by code (2)? ", [1, 2])
    if entry_type == 1:
        del_item = input("What is the name of the item? ")
        del_item = sanitize(del_item)
        del_item = "%"+del_item+"%"
        cur.execute("SELECT * FROM current_trans_{} WHERE pname LIKE {} COLLATE NOCASE".format(cashier, del_item))
    elif entry_type == 2:
        del_item = check_numeric("What is the item code? ", False, "int")
        del_item = str(del_item)
        del_item = "%"+del_item+"%"
        cur.execute("SELECT * FROM current_trans_{} WHERE icode LIKE {}".format(cashier, del_item,))
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
    cur.execute("DELETE FROM current_trans_{} WHERE id = {}".format(cashier, chosen_row_id,))
    print("Deleted entry: {}".format(chosen_row))
    if len(coupon_entries) > 0:
        print("Deleting all coupons related to this item.")
        for i in coupon_entries:
            coupon_entry_id = i[0]
            cur.execute("DELETE FROM current_trans_{} WHERE id = {}".format(cashier, coupon_entry_id,))
    conn.commit()
    conn.close()
    return "Successfully deleted entry."

def void_last(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM current_trans_{}".format(cashier,))
    max_id = cur.fetchone()
    max_id = max_id[0]
    cur.execute("SELECT pname FROM current_trans_{} WHERE id = {}".format(cashier, max_id,))
    pname = cur.fetchone()
    pname = pname[0]
    cur.execute("DELETE FROM current_trans_{} WHERE id = {}".format(cashier, max_id,))
    conn.commit()
    conn.close()
    return "Deleted last {} from the transaction".format(pname)

def void_transaction(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    print("This action requires manager authorization.")
    authorized = manager_auth()
    if authorized:
        cur.execute("SELECT icode, coupon_code, user_weight FROM current_trans_{}".format(cashier,))
        items = cur.fetchall()
        for i in items:
            icode = i[0]
            ccode = i[1]
            quan = i[2]
            if icode == ccode:  # Is this a coupon? If not, proceed.
                cur.execute("UPDATE stock SET quan = quan + ? WHERE code = ?", (quan, icode))
        cur.execute("DELETE FROM current_trans_{}".format(cashier))
        conn.commit()
        return "Transaction canceled."
    else:
        return "Cannot complete."

def view_transaction(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM current_trans_{}".format(cashier))
    transaction = cur.fetchall()
    total_price = 0
    sales_tax = 0
    ebt_price = 0
    ebt_tax = 0
    non_ebt_price = 0
    non_ebt_tax = 0
    re_points = 0
    for i in transaction:
        print(i)
        total_price += i[5]    
        sales_tax += i[6]
        if i[7] == 1:
            ebt_price += i[5]
            ebt_tax+= i[6]
        else:
            non_ebt_price += i[5]
            non_ebt_tax += i[6]
        re_points += i[8]
    ebt_price += ebt_tax
    non_ebt_price += non_ebt_tax
    ebt_price = round(ebt_price, 2)             # Everything needs to be rounded,
    non_ebt_price = round(non_ebt_price, 2)     # or else stupid things might happen.
    total_price = ebt_price + non_ebt_price
    total_price = round(total_price, 2)
    cur.execute("SELECT paid, paid_ebt FROM current_trans_meta WHERE cashier = ?", (cashier,))
    paid_both = cur.fetchall()
    paid_both = paid_both[0]
    paid = paid_both[0]
    paid_ebt = paid_both[1]
    re_points = round(re_points, 0)
    re_points = int(re_points)
    print("""Total due: {}
    Sales tax owed: {}
    Non-EBT balance due: {}
    EBT balance due: {}
    Rewards points gained for this transaction: {}
    Paid so far: {}
    EBT paid so far: {}""".format(
        total_price, sales_tax, non_ebt_price, ebt_price, re_points, paid, paid_ebt
    ))
    return [total_price, sales_tax, non_ebt_price, ebt_price, re_points, paid, paid_ebt]

def payment(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    totals = view_transaction(cashier)
    total_price = totals[0]
    non_ebt_price = totals[2]
    ebt_price = totals[3]
    paid = totals[5]
    paid_ebt = totals[6]
    non_ebt_total = non_ebt_price - paid
    ebt_total = ebt_price - paid_ebt
    final_price = non_ebt_total + ebt_total
    final_price = round(final_price,2)
    while final_price > 0:
        print("Remaining total is {}".format(final_price))
        choice = get_result("Will the customer be paying with credit/debit (1), cash (2), or EBT (3)? Or would you like to cancel (4)? ", [1, 2, 3, 4])
        if choice == 1:
            paying = check_numeric("How much is being paid for with card? (Default is all) ", True, "float")
            if not paying or paying == "not_numeric":
                paying = final_price
            paying = round(paying, 2)
            if paying > non_ebt_total:
                overflow = paying - non_ebt_total
                paying = non_ebt_total
            else:
                overflow = 0
            paying_ebt = 0
            paying_ebt += overflow
            if paying_ebt > ebt_total:
                overflow = paying_ebt - ebt_total
                paying_ebt = ebt_total
            else:
                overflow = 0
            paying = round(paying, 2)
            paying_ebt = round(paying_ebt, 2)
            overflow = round(overflow, 2)
            cur.execute("UPDATE current_trans_meta SET paid = paid + ? WHERE cashier = ?", (paying, cashier))
            if paying_ebt:
                cur.execute("UPDATE current_trans_meta SET paid_ebt = paid_ebt + ? WHERE cashier = ?", (paying_ebt, cashier))
            if overflow:
                cur.execute("UPDATE current_trans_meta SET overflow = ? WHERE cashier = ?", (overflow, cashier))
            conn.commit()
            non_ebt_total -= paying
            ebt_total -= paid_ebt
        elif choice == 2:
            dollars = [1, 5, 10, 20, 50, 100]
            nearest_dollar = math.ceil(total_price)     # This rounds up the total to the nearest whole dollar.
            if nearest_dollar in dollars:               # Is this number in the dollars list? If it is, then we 
                possible_dollars = []                   # don't want to put that particular variable first.
            else:                                       # No? Then we will put it there.
                possible_dollars = [nearest_dollar]
            for i in dollars:                           # Only includes amounts that are higher than the total.
                if i > total_price:
                    possible_dollars.append(i)
            if possible_dollars[0] > 20:                # This part finds the minimum number of $20 bills that
                twenties = 40                           # will cover the cost. They're the most common 
                while twenties < total_price:           # denomination I work with besides $1s, so I felt this
                    twenties += 20                      # feature would be useful.
                if twenties != 100:                     # This part prevents it from creating a duplicate
                    possible_dollars.insert(1, twenties)# $100 entry.
            len_of_possibs = len(possible_dollars)
            len_of_possibs += 3
            number_of_possibs = 1
            print("Which of the following dollar amounts are being used:")
            print("Number 1: Exact Change")             # There's always the possibility they'll give you exact change.
            for j in possible_dollars:                  # I didn't feel like finding out if I could reuse i.
                number_of_possibs += 1
                print("Number {}: {}".format(number_of_possibs,j))
            number_of_possibs += 1
            print("Number {}: Custom".format(number_of_possibs))    # They also might give you a totally random amount.
            result_possibs = range(1, len_of_possibs, 1)
            select_amount = get_result("Enter your choice: ", result_possibs)
            if select_amount == 1:
                paying = total_price
            elif select_amount == number_of_possibs:
                paying = check_numeric("How much is the customer paying with? ", False, "float")
                if paying == "not_numeric":
                    return "Error: Please enter a number."
                paying = round(paying,2)
            else:
                paying = possible_dollars[select_amount-2]
            paying = round(paying, 2)
            if paying > non_ebt_total:
                overflow = paying - non_ebt_total
                paying = non_ebt_total
            else:
                overflow = 0
            paying_ebt = 0
            paying_ebt += overflow
            if paying_ebt > ebt_total:
                overflow = paying_ebt - ebt_total
                paying_ebt = ebt_total
            else:
                overflow = 0
            paying = round(paying, 2)
            paying_ebt = round(paying_ebt, 2)
            overflow = round(overflow, 2)
            cur.execute("UPDATE current_trans_meta SET paid = paid + ? WHERE cashier = ?", (paying, cashier))
            if paying_ebt:
                cur.execute("UPDATE current_trans_meta SET paid_ebt = paid_ebt + ? WHERE cashier = ?", (paying_ebt, cashier))
            if overflow:
                cur.execute("UPDATE current_trans_meta SET overflow = ? WHERE cashier = ?", (overflow, cashier))
            conn.commit()
            non_ebt_total -= paying
            ebt_total -= paid_ebt
        elif choice == 3:
            paying = check_numeric("How much is being paid for with EBT? (Default is all) ", True, "float")
            if not paying or paying == "not_numeric":
                paying = ebt_price
            paying = round(paying,2)
            cur.execute("UPDATE current_trans_meta SET paid_ebt = ?", (paying,))
            conn.commit()
        else:
            return "Exiting."
        cur.execute("SELECT paid, paid_ebt FROM current_trans_meta WHERE cashier = ?", (cashier,))
        paid_data = cur.fetchall()
        paid_data = paid_data[0]
        paid = paid_data[0]
        paid_ebt = paid_data[1]
        non_ebt_total = non_ebt_price - paid
        ebt_total = ebt_price - paid_ebt
        final_price = non_ebt_total + ebt_total
        final_price = round(final_price,2)
    cur.execute("SELECT overflow FROM current_trans_meta WHERE cashier = ?", (cashier,))
    change = cur.fetchone()
    change = change[0]
    change = round(change,2)
    print("The transaction is over! Change due is {}".format(change))
    return finish_transaction(cashier)

def finish_transaction(cashier):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM current_trans_{}".format(cashier))
    transaction = cur.fetchall()
    if not transaction:
        return "There is no transaction to finish."
    dt = datetime.now()                         # Getting the current time to print on the receipt,
    codedt = dt.strftime("%Y%m%d-%H%M%S-{}".format(cashier))    # and for the receipt's filename.
    verbdt = dt.strftime("%A, %B %d, %Y")
    cur.execute("SELECT cashier_fname FROM current_trans_meta WHERE cashier = ?", (cashier,))
    cashier_name = cur.fetchone()
    cashier_name = cashier_name[0]
    your_cashier = "Your cashier was {}".format(cashier_name)
    all_depts = [["DEEP BLUE", "", "-----"], ["", "- Produce"], ["", "- Meat"], ["", "- Deli"],
    ["", "- Dairy"], ["", "- Frozen"], ["", "- Grocery"], ["", "- Miscellaneous"],[]]
    total_sales_tax = 0     # all_depts will hold all the text data which will be printed
    total_price = 0         # onto the receipt. Is doing it this way insane?
    total_savings = 0       # Well, maybe. Possibly even probably.
    total_points = 0.0
    for i in transaction:   # The empty list entries will be made into blank lines.
        name = i[1]
        icode = i[2]
        ccode = i[11]
        quantity = round(i[3], 2)
        price = round(i[4], 2)
        final_price = round(i[5], 2)
        sales_tax = round(i[6], 2)
        points = round(i[8], 2)
        total_price = total_price + final_price + sales_tax
        if final_price < 0:
            final_price = abs(final_price)
            total_savings += final_price
        total_sales_tax += sales_tax
        total_points += points
        cur.execute("SELECT department FROM stock WHERE code = ?", (icode,))
        dept = cur.fetchone()   # The current_transaction table doesn't store the department,
        dept = dept[0]          # since that's not really relevant to the transaction in progress.
        cur.execute("SELECT ccode FROM interim_trans_{} WHERE ccode = {}".format(cashier, ccode))
        test = cur.fetchone()   # I didn't know how to do what I had in mind with just the nested lists above,
        if test:                # so I figured I'd just put the stuff in a separate table and process it like that.
            cur.execute("UPDATE interim_trans_{} SET quantity = quantity + {}, final_price = final_price + {} WHERE ccode = {}".format(
                cashier, quantity, final_price, ccode
            ))
        else:
            cur.execute("INSERT INTO interim_trans_{} VALUES('{}',{},{},{},{},{},{})".format(
                cashier, name, icode, ccode, quantity, price, final_price, dept))
        conn.commit()
    total_sales_tax = round(total_sales_tax, 2)     # The receipt looks stupid if I don't round at every opportunity.
    total_price = round(total_price, 2)
    total_savings = round(total_savings, 2)
    total_sales_tax_text = "Sales tax: ${}".format(total_sales_tax)
    total_price_text = "Total price: ${}".format(total_price)
    total_savings_text = "You saved ${}".format(total_savings)
    cur.execute("SELECT disc_card FROM current_trans_meta WHERE cashier = ?", (cashier,))
    rewards_card = cur.fetchone()
    rewards_card = rewards_card[0]
    if rewards_card:
        total_points = round(total_points, 0)
        total_points = int(total_points)
        earned_points_text = "You earned {} points".format(total_points)
        cur.execute("SELECT points FROM cards WHERE phone = ?", (rewards_card,))
        current_points = cur.fetchone()
        if current_points:
            current_points = current_points[0]
        else:
            current_points = 0
        current_points += total_points
        current_points_text = "You now have {} total points".format(current_points)
        if total_savings > 0:   # This code appends the sales tax, total price, savings, and earned points onto the end of the receipt.
            all_depts[8].extend(["", total_sales_tax_text, total_price_text, total_savings_text, earned_points_text, current_points_text, verbdt, your_cashier])
        else:                   # If there were no points earned, it only gives the current points.
            all_depts[8].extend(["", total_sales_tax_text, total_price_text, earned_points_text, current_points_text, verbdt, your_cashier])
    elif total_savings > 0:     # If there was no card, but there were savings, it omits everything related to points.
        all_depts[8].extend(["", total_sales_tax_text, total_price_text, total_savings_text, verbdt, your_cashier])
    else:                       # If there was no card or savings, it omits both.
        all_depts[8].extend(["", total_sales_tax_text, total_price_text, verbdt, your_cashier])
    cur.execute("SELECT icode, ccode FROM interim_trans_{}".format(cashier))
    ccodes = cur.fetchall() # Returns a list of tuple pairs, like [(4011, 4011)...]
    for i in ccodes:
        if i[0] == i[1]:    # Is this a coupon? If not, proceed.
            ccode = i[1]
            cur.execute("SELECT name, quantity, final_price, dept FROM interim_trans_{} WHERE ccode = {}".format(cashier, ccode))
            things = cur.fetchall()
            things = things[0]
            interim_price = things[2]
            department = things[3]  # Item name: Quantity $Price
            sentence = "{}: {} ${}".format(things[0], things[1], interim_price)
            all_depts[department].append(sentence)
            cur.execute("SELECT name, final_price FROM interim_trans_{} WHERE icode = {} AND icode != ccode".format(cashier, ccode))
            coupon = cur.fetchall()
            if coupon:
                coupon = coupon[0]
                coupon_savings = coupon[1]
                sentence = "{}: ${}".format(coupon[0], coupon_savings)
                all_depts[department].append(sentence)
                total_savings = interim_price - coupon_savings
                total_savings = round(total_savings, 2)
                sentence = "Your price: ${}".format(total_savings)
                all_depts[department].append(sentence)
    save_dir = "receipts/"
    filename = "receipt_{}.txt".format(codedt)
    save_location = os.path.join(save_dir, filename)
    file = open(save_location, "a")
    for j in all_depts:
        if len(j) > 2:
            for k in j:
                print(k)
                if "cashier" in k:              # Just so there isn't a newline at the very end.
                    file.write("{}".format(k))  # A bit hacky, but it works.
                else:
                    file.write("{}\n".format(k))
    #cur.execute("SELECT icode, ccode, quantity FROM interim_trans_{}".format(cashier))
    #to_lower = cur.fetchall()
    #for k in to_lower:
    #    if k[0] == k[1]:    # Is this a coupon? If not, proceed.
    #        item_code = k[1]# Just so we know what's going on.
    #        quan_lower = k[2]
    #        cur.execute("UPDATE stock SET quan = quan - ? WHERE code = ?", (quan_lower, item_code))
    cur.execute("DELETE FROM current_trans_{}".format(cashier))
    cur.execute("DELETE FROM interim_trans_{}".format(cashier))
    cur.execute("""UPDATE current_trans_meta
    SET disc_card = 0,
    cust_age = 0,
    paid = 0,
    paid_ebt = 0,
    overflow = 0
    WHERE cashier = ?""", (cashier,))
    if rewards_card:
        cur.execute("UPDATE cards SET points = ? WHERE phone = ?", (current_points, rewards_card))
    conn.commit()
    return "Transaction finished. Have a nice day!"