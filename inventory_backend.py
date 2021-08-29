import sqlite3
import dateutil.parser as parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from core_backend import *

def insert_coupon(): 
    name = input("What is the name of the coupon? ")
    code = check_numeric("What is the coupon's code: (Leave blank to auto-generate) ", True, "int")
    if not code or code == "not_numeric":
        print("Auto-generating coupon code...")
        code = generate_code("coupons")
    elif code == "not_numeric":
        print("Incorrect input. Auto-generating coupon code...")
        code = generate_code("coupons")
    if code == "invalid_table":
        return "Wrong table type. Please check the script."
    print("Coupon code is %s" % code)
    icode = check_numeric("What is the item code affected by the coupon? ", False, "int")
    if icode == "not_numeric":
        return "Invalid item code."
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM coupons WHERE item_code = ?", (icode,))
    existing = cur.fetchall()   # I would use a function for this, but it's only being done twice.
    if len(existing) > 0:       # Maybe if I have to do it a third time, I'll make a function.
        print("The specified item code already has a coupon associated with it:\n{}".format(existing))
        should = get_true("Would you like to continue? (Default is no) ", 0)
        if should == 0:
            return "Item code already in use. Exiting."
    conn.close()
    disctype = get_result("Is this coupon a fixed discount (1), a percent off(2), or a new price (3)?  ",(1,2,3))
    if disctype == "wrong":
        return "Invalid discount type."
    discval = check_numeric("What is the coupon's value? ", False, "float")
    if discval == "not_numeric":
        return "Invalid discount value."
    minquant = check_numeric("How many items are needed for the coupon? (Default is 0.01) ", True, "float")
    if not minquant or minquant == "not_numeric":
        minquant = 0.01
    maxquant = check_numeric("What is the maximum number of times this coupon can be applied? (Default is infinite) ", True, "int")
    if not maxquant or maxquant == "not_numeric": # I know I could probably do the same thing with .isnumeric,
        maxquant = 0                              # but I like having it be this verbose. A little easier to see what's going on.
    doubled = get_true("Should the coupon be doubled? (Default is no) ", 0)
    disccard = get_true("Is this coupon exclusive to rewards card members? (Default is no) ", 0)
    if disccard == 1:
        points = check_numeric("What is the reward point cost for this coupon? (Default is 0) ", True, "int")
        if not points or points == "not_numeric":
            points = 0
    else:
        print("There will be no reward point cost for this coupon.")
        points = 0
    predate = get_result("Will this coupon expire on a day (1), in some period of time (2), or never (3)? ",(1,2,3))
    if predate == 1:
        predate = input("On what day will the coupon expire? ")
        predate = parser.parse(predate)
        expdate = predate.isoformat()
    elif predate == 2:
        dwmy = get_result("Will this coupon expire in days (1), weeks (2), months (3), or years (4)? ", (1,2,3,4))
        future_val = check_numeric("In how many of these will the coupon expire? ", False, "int")
        if future_val == "not_numeric":
            return "Invalid time unit count."
        if dwmy == 1:
            td = timedelta(days=future_val)
        elif dwmy == 2:
            td = timedelta(weeks=future_val)
        elif dwmy == 3:
            td = relativedelta(months=+future_val)
        elif dwmy == 4:
            td = relativedelta(years=+future_val)
        dt = datetime.now()
        procdate = td + dt
        expdate = procdate.isoformat()
    else:
        expdate = 0
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO coupons VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)",
    (name,code,icode,disctype,discval,minquant,maxquant,doubled,disccard,expdate,points))
    conn.commit()
    conn.close()
    return """Inserted coupon.
    Coupon name: {}
    Coupon ID: {}
    Item ID affected by coupon: {}
    Coupon by each/weight (1), percent off (2), or new price (3): {}
    Value: {}
    Minimum items for coupon: {}
    Maximum applications of this coupon: {}
    Should the coupon be doubled: {}
    Is the coupon only available to rewards card members: {}
    Expiration date: {}
    Rewards point cost: {}""".format(name,code,icode,disctype,discval,minquant,maxquant,doubled,disccard,points,expdate)

def insert_customer():
    fname = input("What is the customer's first name? ").capitalize()
    lname = input("What is the customer's last name? ").capitalize()
    phone = check_phone()
    if phone == "exists":
        return "Invalid phone number."
    code = generate_code("cards")
    if code == "invalid_table":
        return "Wrong table type. Please check the script."
    print("Automatically generated customer code is %s" % code)
    points = check_numeric("How many rewards points should the customer start with? (Default is 0) ", True, "int")
    if not points or points == "not_numeric":
        points = 0
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO cards VALUES (NULL,?,?,?,?,?)",(fname,lname,phone,code,points))
    conn.commit()
    conn.close()
    return """Added rewards card member.
    First name: {}
    Last name: {}
    Phone number: {}
    Reference code: {}
    Rewards point balance: {}""".format(fname,lname,phone,code,points)

def insert_product():
    name = input("What is the product's name? ")
    code = check_codes("What is the product's code number or PLU? ")
    if code == "exists":
        return "The specified item code already exists. Please use another one."
    elif code == "no_result":
        return "Error: No item code specified. Exiting."
    elif code == "not_numeric":
        return "Error: Codes must be numeric. Please enter a number."
    weigh = get_true("Should this item be sold by weight? (Default is no) ", 0)
    quan = check_numeric("How much/many of the product do you have? ", False, "float")
    if quan == "not_numeric":
        return "Invalid item quantity."
    low_quan = check_numeric("How much/many of the product should be considered low stock? ", False, "float")
    if low_quan == "not_numeric":
        return "Invalid low quantity value."
    restock = get_true("Do you want to restock this item? (Default is yes) ", 1)
    if weigh == 1:
        print("The cashier will be asked to weigh this item.")
        spec_quant = 1
    else:
        spec_quant = get_true("Do you want the cashier to specify a quantity of this item? (Default is no) ", 0)
    price = check_numeric("How much will this item cost, by each or by weight? ", False, "float")
    if check_numeric == "not_numeric":
        return "Invalid price entry."
    price = round(price, 2)
    tax = get_true("Is this item subject to sales tax? (Default is no) ", 0)
    ebt = get_true("Is this item available to puchase with food stamps? (Default is yes) ", 1)
    re_points = get_true("Does purchasing this item count towards rewards points? (Default is yes) ", 1)
    age = check_numeric("What is the minimum age to purchase this item? Default is 0: ", True, "int")
    if not age or age == "not_numeric" :
        age = 0
    disc_price = check_numeric("What should the rewards card price be? Default is same as regular price: ", True, "float")
    if not disc_price or disc_price == "not_numeric":
        disc_price = price
    department = get_result("What kind of item is this: Produce (1), Meat (2), Deli (3), Dairy (4), Frozen (5), Grocery (6), Miscellaneous (7)? ", [1, 2, 3, 4, 5, 6, 7])
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO stock VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (name,code,weigh,quan,low_quan,restock,spec_quant,price,tax,
                ebt,re_points,age,disc_price,department))
    conn.commit()
    conn.close()
    return ("""Inserted product.
        Name: {}
        Code number or PLU: {}
        Sold by weight: {}
        Quantity in stock: {}
        Low stock threshold: {}
        Should it be restocked: {}
        Should the cashier specify a quantity: {}
        Price: {}
        Taxable: {}
        Purchasable with food stamps: {}
        Counts towards rewards points: {}
        Minimum age to purchase: {}
        Store card discounted price: {}
        Department: {}""".format(name, code, weigh, quan, low_quan, restock,
        spec_quant, price, tax, ebt, re_points, age, disc_price,department))

def insert_employee():
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    fname = input("What is the employee's first name? ")
    fname = sanitize(fname)
    lname = input("What is the employee's last name? ")
    lname = sanitize(lname)
    cur.execute("SELECT * FROM employees WHERE fname LIKE ? AND lname LIKE ? COLLATE NOCASE", (fname, lname))
    same = cur.fetchall()
    if same:
        if fname in same[0] and lname in same[0]:
            print("This user appears to already exist:\n{}".format(same))
            confirm = get_true("Would you like to create the account anyway? (Default is no) ", 0)
            if confirm == 0:
                return "User already exists. Exiting."
    actype = get_result("Is this employee a cashier (1) or a manager (2)? ", [1, 2])
    if actype == "wrong":
        return "Invalid account type."
    if actype == 1:
        text_actype = "Cashier"
    else:
        text_actype = "Manager"
    login = stop_dupe("What is the user's login code? ", "employees", "login")
    if login == "item_exists":
        return "Login code already exists. Exiting."
    passcode = check_numeric("What is the user's passcode? (Default is same as login code) ", True, "int")
    if passcode == "not_numeric": # pass is already a Python thing, so I'm using this instead.
        passcode = login
    cur.execute("INSERT INTO employees VALUES (NULL,?,?,?,?,?)", (fname, lname, actype, login, passcode))
    cur.execute("""CREATE TABLE IF NOT EXISTS current_trans_{}(
    id INTEGER PRIMARY KEY,
    pname TEXT,
    icode INTEGER,
    user_weight REAL,
    price REAL,
    final_price REAL,
    product_tax REAL,
    ebt_paid INTEGER,
    rewards_points REAL,
    price_delta REAL,
    req_points INTEGER,
    coupon_code INTEGER
    )""".format(login))
    conn.commit()
    conn.close()
    return """Inserted employee:
    First name: {}
    Last name: {}
    Account type: {}
    Login code: {}
    Passcode: {}""".format(fname,lname,text_actype,login,passcode)

def update_coupon():
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    search = input("What coupon would you like to view?\nEnter a code or a name, or blank for all: ")
    rows = view(search, "coupons")

    if isinstance(rows, list) == False:
        return rows
    len_rows = len(rows)
    if len_rows == 1:
        selected_row = 0
        final_row = rows[selected_row]
        print("Using this entry:\n", final_row)
    else:
        seq = 1
        for i in rows:
            print("Number %s: %s" % (seq, i))
            seq = seq + 1
        len_rows = len_rows + 1
        avail_rows = [*range(1, len_rows, 1)]
        selected_row = get_result("Which entry would you like to modify? ", avail_rows)
        selected_row = selected_row - 1
        final_row = rows[selected_row]
    row_id = final_row[0]

    print("""Which of the following would you like to update:
        Coupon name (1)
        Code (2)
        Affected item code (3)
        Type of discount(4)
        Value (5)
        Minimum items for the coupon (6)
        Maximum items for the coupon (7)
        Whether or not the coupon is doubled (8)
        Whether or not the coupon requires a discount card (9)
        The expiration date (10)
        The rewards point cost (11)""")
    options = [*range(1, 12, 1)]                                # The second number has to be 1 greater than the intended size,
    var_to_use = get_result("Enter your selection: ", options)  # otherwise it won't let you use the last option.
    if not isinstance(var_to_use, int):
        return var_to_use

    if var_to_use == 1:                                                  # I would just use one cur.execute, but the name is vulnerable to SQL injection.
        cur.execute("SELECT name FROM coupons WHERE id = ?", (row_id,)) # Plus, all these different variables need to be treated differently.
        old_val = cur.fetchone() # Setting up for a comparison at the end.
        new_val = input("What is the new name of the coupon? ")
        cur.execute("UPDATE coupons SET name = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 2:
        cur.execute("SELECT code FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_codes("What is the new coupon code? ")
        if new_val == "exists":
            return "Invalid coupon code."
        cur.execute("UPDATE coupons SET code = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 3:
        cur.execute("SELECT item_code FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What item code should the coupon affect? ", False, "int")
        if new_val == "not_numeric":
            return "Invalid item code."
        cur.execute("SELECT * FROM coupons WHERE item_code = ?", (new_val,))
        existing = cur.fetchall()
        if len(existing) > 0:
            print("The specified item code already has a coupon associated with it:\n{}".format(existing))
            should = get_true("Would you like to continue? (Default is no) ", 0)
            if should == 0:
                return "Item code already in use. Exiting."
        cur.execute("UPDATE coupons SET item_code = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 4:
        cur.execute("SELECT each_weigh FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_result("Is this coupon a fixed discount (1), a percent off(2), or a new price (3)? ",(1,2,3))
        if new_val == "Invalid input.":
            return new_val
        cur.execute("UPDATE coupons SET each_weigh = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 5:
        cur.execute("SELECT value FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the new coupon value? ", False, "float")
        if new_val == "not_numeric":
            return "Invalid coupon value."
        cur.execute("SELECT each_weigh FROM coupons WHERE id = ?", (row_id,))
        coupon_type = cur.fetchone()
        coupon_type = coupon_type[0]
        cur.execute("SELECT item_code FROM coupons WHERE id = ?", (row_id,))
        icode = cur.fetchone()
        icode = icode[0]
        cur.execute("SELECT price FROM stock WHERE code = ?", (icode,))
        orig_price = cur.fetchone()
        orig_price = orig_price[0]
        if not coupon_type == 2 and new_val > orig_price:
            print("The coupon's value ({}) seems to be higher than the price of the item({})".format(new_val, orig_price))
            decision = get_true("Would you like to keep the coupon value? (Default is no) ", 0)
            if decision == 0:
                return "Coupon value exceeds item price. Exiting."
        cur.execute("UPDATE coupons SET value = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 6:
        cur.execute("SELECT min FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the new minimum items for the coupon? (Default is 0.01) ", True, "float")
        if new_val == "not_numeric" or not new_val:
            new_val = 0.01
        cur.execute("UPDATE coupons SET min = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 7:
        cur.execute("SELECT max FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the maximum number of times this coupon may be applied? (Default is infinite) ", True, "float")
        if new_val == "not_numeric" or not new_val:
            new_val = "0"
        cur.execute("UPDATE coupons SET max = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 8:
        cur.execute("SELECT doubled FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Should this coupon be doubled? (Default is no) ", 0)
        cur.execute("UPDATE coupons SET doubled = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 9:
        cur.execute("SELECT disc_card FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Should this coupon be exclusive to rewards card members? (Default is no) ", 0)
        cur.execute("UPDATE coupons SET disc_card = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 10:
        cur.execute("SELECT expire FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        predate = get_result("Will this coupon expire on a day (1), in some period of time (2), or never (3)? ", (1,2,3))
        if predate == 1:
            predate = input("On what day will the coupon expire? ")
            predate = parser.parse(predate)
            new_val = predate.isoformat()
        elif predate == 2:
            dwmy = get_result("Will this coupon expire in days (1), weeks (2), months (3), or years (4)?", (1,2,3,4))
            future_val = check_numeric("In how many of these will the coupon expire? ", False, "int")
            if future_val == "not_numeric":
                return "Invalid time unit count."
            if dwmy == 1:
                td = timedelta(days=future_val)
            elif dwmy == 2:
                td = timedelta(weeks=future_val)
            elif dwmy == 3:
                td = timedelta(months=future_val)
            elif dwmy == 4:
                td = timedelta(years=future_val)
            dt = datetime.now()
            procdate = td + dt
            new_val = procdate.isoformat()
        else:
            new_val = 0
        cur.execute("UPDATE coupons SET expire = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 11:
        cur.execute("SELECT re_cost FROM coupons WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the rewards point cost of this coupon? (Default is none) ", True, "int")
        if new_val == "not_numeric" or not new_val:
            new_val = 0
        cur.execute("UPDATE coupons SET re_cost = ? WHERE id = ?", (new_val, row_id))
    else:
        return "Please choose an entry to change."
    old_val = old_val[0]
    print("Old value: {}\nNew value: {}".format(old_val,new_val))
    decision = get_true("Are you sure you want to make this change? (Default is yes) ", 1)
    if decision == 1:
        conn.commit()
        finality = "Change saved."
    else:
        finality = "Change not saved."
    conn.close()
    return finality

def update_customer():
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    search = input("What customer would you like to view?\nEnter a code or a name, or blank for all: ")
    rows = view(search, "cards")

    if isinstance(rows, list) == False:
        return rows
    len_rows = len(rows)
    if len_rows == 1:
        selected_row = 0
        final_row = rows[selected_row]
        print("Using this entry:\n", final_row)
    else:
        seq = 1
        for i in rows:
            print("Number %s: %s" % (seq, i))
            seq = seq + 1
        len_rows = len_rows + 1
        avail_rows = [*range(1, len_rows, 1)]
        selected_row = get_result("Which entry would you like to modify? ", avail_rows)
        selected_row = selected_row - 1
        final_row = rows[selected_row]
    row_id = final_row[0]

    print("""Which of the following would you like to update:
        First name (1)
        Last name (2)
        Phone number (3)
        Code (4)
        Rewards points balance (5)""")
    options = [*range(1, 6, 1)]                                 # The second number has to be 1 greater than the intended size,
    var_to_use = get_result("Enter your selection: ", options)  # otherwise it won't let you use the last option.
    if not isinstance(var_to_use, int):
        return var_to_use

    if var_to_use == 1:                                                 
        cur.execute("SELECT fname FROM cards WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = input("What is the customer's first name? ")
        cur.execute("UPDATE cards SET fname = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 2:
        cur.execute("SELECT lname FROM cards WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = input("What is the customer's last name? ")
        cur.execute("UPDATE cards SET lname = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 3:
        cur.execute("SELECT phone FROM cards WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_phone()
        if new_val == "exists":
            return "Invalid phone number."
        cur.execute("UPDATE cards SET phone = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 4:
        cur.execute("SELECT code FROM cards WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_codes("What should the customer's card code be? ")
        if new_val == "exists":
            return "Code already in use. Please select another one."
        cur.execute("UPDATE cards SET code = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 5:
        cur.execute("SELECT points FROM cards WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What should be the customer's rewards point balance? ", False, "int")
        if new_val == "not_numeric":
            return "Invalid rewards points value."
        cur.execute("UPDATE cards SET points = ? WHERE id = ?", (new_val, row_id))
    else:
        return "Please choose an entry to change."
    old_val = old_val[0]
    print("Old value: {}\nNew value: {}".format(old_val,new_val))
    decision = get_true("Are you sure you want to make this change? (Default is yes) ", 1)
    if decision == 1:
        conn.commit()
        finality = "Change saved."
    else:
        finality = "Change not saved."
    conn.close()
    return finality

def update_stock():
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    search = input("What item would you like to view?\nEnter a code or a name, or blank for all: ")
    rows = view(search, "stock")

    if isinstance(rows, list) == False: # view will return either a list or a string. If it's not a list, there's an error.
        return rows
    len_rows = len(rows)
    if len_rows == 1:
        selected_row = 0
        final_row = rows[selected_row]
        print("Using this entry:\n", final_row)
    else:
        seq = 1
        for i in rows:
            print("Number %s: %s" % (seq, i))
            seq = seq + 1
        len_rows = len_rows + 1
        avail_rows = [*range(1, len_rows, 1)]
        selected_row = get_result("Which entry would you like to modify? ", avail_rows)
        selected_row = selected_row - 1
        final_row = rows[selected_row]
    row_id = final_row[0]

    print("""Which of the following would you like to update:
        Item name (1)
        Code (2)
        If the product is sold by weight (3)
        Quantity available (4)
        Low quantity threshold (5)
        Should the item be restocked (6)
        Should the cashier specify a quantity (7)
        Price (8)
        If the item is subject to sales tax (9)
        If the item is available with food stamps (10)
        Should the item yield rewards points (11)
        Minimum age to purchase the item (12)
        Discount card price (13)
        Department (14)""")
    options = [*range(1, 15, 1)]
    var_to_use = get_result("Enter your selection: ", options)
    if not isinstance(var_to_use, int):
        return var_to_use

    if var_to_use == 1:                                                # I would just use one cur.execute, but the name is vulnerable to SQL injection.
        cur.execute("SELECT name FROM stock WHERE id = ?", (row_id,)) # Plus, all these different variables need to be treated differently.
        old_val = cur.fetchone()    # Setting up for a comparison at the end.
        new_val = input("What is the new name of the item? ")
        cur.execute("UPDATE stock SET name = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 2:
        cur.execute("SELECT code FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_codes("What is the new item code? ")
        if new_val == "exists":
            return "Invalid item code."
        cur.execute("UPDATE stock SET code = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 3:
        cur.execute("SELECT weigh FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Should the item be sold by weight? (Default is no) ", 0)
        cur.execute("SELECT spec_quant FROM stock WHERE id = ?", (row_id,))
        spec_quant = cur.fetchone()
        spec_quant = spec_quant[0] # Even with fetchone, it returns a tuple. This extracts the value.
        if spec_quant == 0 and new_val == 1:
            should = get_true("The cashier must specify a weight on items sold by weight.\nWould you like to continue with this change? (Default is yes) ", 1)
            if should == 1:
                cur.execute("UPDATE stock SET spec_quant = 1 WHERE id = ?", (row_id,))
            else:
                return "This change is too dangerous to perform. Exiting."
        cur.execute("UPDATE stock SET weigh = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 4:
        cur.execute("SELECT quan FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("How much/many of this item is in stock? ", False, "float")
        if new_val == "not_numeric":
            return "Invalid quantity."
        cur.execute("UPDATE stock SET quan = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 5:
        cur.execute("SELECT low_quan FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the new low stock threshold? ", False, "float")
        if new_val == "not_numeric":
            return "Invalid low stock value."
        cur.execute("UPDATE stock SET low_quan = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 6:
        cur.execute("SELECT restock FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Should this item be restocked? (Default is yes) ", 1)
        cur.execute("UPDATE stock SET restock = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 7:
        cur.execute("SELECT spec_quant FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Should the cashier specify a quantity of the item? (Default is no) ", 0)
        cur.execute("SELECT weigh FROM stock WHERE id  = ?", (row_id,))
        weigh = cur.fetchone()
        weigh = weigh[0]
        if weigh == 0 and new_val == 1:
            should = get_true("Should this item be sold by weight? (Default is no) ", 0)
        if weigh == 1 and new_val == 0:
            should = get_true("Items sold by weight must have a weight specified.\nShould this item be sold by weight? (Default is no) ", 0)
            if should == 1:
                return "This change is too dangerous to perform. Exiting."
        cur.execute("UPDATE stock SET weigh = ? WHERE id = ?", (should, row_id))
        cur.execute("UPDATE stock SET spec_quant = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 8:
        cur.execute("SELECT price FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the price of this item? ", False, "float")
        if new_val == "not_numeric":
            return "Invalid price."
        cur.execute("UPDATE stock SET price = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 9:
        cur.execute("SELECT tax FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Is this item subject to sales tax? (Default is no) ", 0)
        cur.execute("UPDATE stock SET tax = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 10:
        cur.execute("SELECT ebt FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Is this item available to puchase with food stamps? (Default is no) ", 0)
        cur.execute("UPDATE stock SET ebt = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 11:
        cur.execute("SELECT re_points FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Does purchasing this item count towards rewards points? (Default is yes) ", 1)
        cur.execute("UPDATE stock SET re_points = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 12:
        cur.execute("SELECT age FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the minimum age to purchase this item? (Default is 0) ", True, "int")
        if not new_val or new_val == "not_numeric":
            new_val = 0
        cur.execute("UPDATE stock SET age = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 13:
        cur.execute("SELECT disc_price FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What should the rewards card price be? Default is same as regular price: ", True, "float")
        cur.execute("SELECT price FROM stock WHERE id = ?", (row_id,))
        normal_price = cur.fetchone()
        normal_price = normal_price[0]
        if new_val and not new_val == "not_numeric" and normal_price < new_val:
            print("The specified rewards card price of {} is higher than the normal price of {}.".format(new_val, normal_price))
            should = get_true("Would you like to make the rewards card price the same as the normal price? (Default is yes) ", 1)
            if should == 1:
                new_val = normal_price
        if not new_val or new_val == "not_numeric":
            cur.execute("SELECT price FROM stock WHERE id = ?", (row_id,))
            new_val = cur.fetchone()
            new_val = new_val[0]
    elif var_to_use == 14:
        cur.execute("SELECT department FROM stock WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_result("What kind of item is this: Produce (1), Meat (2), Deli (3), Dairy (4), Frozen (5), Grocery (6), Miscellaneous (7)? ", [1, 2, 3, 4, 5, 6, 7])
        if new_val == "wrong":
            return "Invalid department."
        cur.execute("UPDATE stock SET department = ? WHERE id = ?", (new_val, row_id))
    else:
        return "Please choose an entry to change."
    old_val = old_val[0]
    print("Old value: {}\nNew value: {}".format(old_val,new_val))
    decision = get_true("Are you sure you want to make this change? (Default is yes) ", 1)
    if decision == 1:
        conn.commit()
        finality = "Change saved."
    else:
        finality = "Change not saved."
    conn.close()
    return finality

def update_employee():
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    search = input("What employee/type would you like to view?\nEnter a code or a name, or blank for all: ")
    rows = view(search, "employees")

    if isinstance(rows, list) == False:
        return rows
    len_rows = len(rows)
    if len_rows == 1:
        selected_row = 0
        final_row = rows[selected_row]
        print("Using this entry:\n", final_row)
    else:
        seq = 1
        for i in rows:
            print("Number %s: %s" % (seq, i))
            seq = seq + 1
        len_rows = len_rows + 1
        avail_rows = [*range(1, len_rows, 1)]
        selected_row = get_result("Which entry would you like to modify? ", avail_rows)
        selected_row = selected_row - 1
        final_row = rows[selected_row]
    row_id = final_row[0]

    print("""Which of the following would you like to update:
        First name (1)
        Last name (2)
        Account type (3)
        Login code (4)
        Passcode (5)""")
    options = [*range(1, 6, 1)]                                 # The second number has to be 1 greater than the intended size,
    var_to_use = get_result("Enter your selection: ", options)  # otherwise it won't let you use the last option.
    if not isinstance(var_to_use, int):
        return var_to_use

    if var_to_use == 1:                                                 
        cur.execute("SELECT fname FROM employees WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = input("What is the employee's first name? ")
        cur.execute("UPDATE employees SET fname = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 2:
        cur.execute("SELECT lname FROM employees WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = input("What is the employee's last name? ")
        cur.execute("UPDATE employees SET lname = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 3:
        cur.execute("SELECT actype FROM employees WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_result("Is this employee a cashier (1) or a manager (2)? ", [1, 2])
        if new_val == "wrong":
            return "Invalid employee type."
        cur.execute("UPDATE employees SET actype = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 4:
        cur.execute("SELECT login FROM employees WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = stop_dupe("What should the user's login code be? ", "employees", "login")
        if new_val == "item_exists":
            return "Login code already exists. Exiting."
        cur.execute("UPDATE employees SET login = ? WHERE id = ?", (new_val, row_id))
    elif var_to_use == 5:
        cur.execute("SELECT passcode FROM employees WHERE id = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What should be the employee's passcode? (Default is same as login code) ", True, "int")
        if new_val == "not_numeric":
            cur.execute("SELECT login FROM employees WHERE id = ?", (row_id,))
            new_val = cur.fetchone()
            new_val = new_val[0]
        cur.execute("UPDATE employees SET passcode = ? WHERE id = ?", (new_val, row_id))
    else:
        return "Please choose an entry to change."
    old_val = old_val[0]
    if isinstance(new_val, str):
        new_val = sanitize(new_val)
    print("Old value: {}\nNew value: {}".format(old_val,new_val))
    decision = get_true("Are you sure you want to make this change? (Default is yes) ", 1)
    if decision == 1:
        if var_to_use == 4:     # Please do not change the cashier's ID in the middle of a transaction. The data will be lost.
            cur.execute("DROP TABLE current_trans_{}".format(old_val))
            cur.execute("""CREATE TABLE IF NOT EXISTS current_trans_{}(
            id INTEGER PRIMARY KEY,
            pname TEXT,
            icode INTEGER,
            user_weight REAL,
            price REAL,
            final_price REAL,
            product_tax REAL,
            paid_ebt INTEGER,
            rewards_points REAL,
            price_delta REAL,
            req_points INTEGER,
            coupon_code INTEGER
            )""".format(new_val))
        conn.commit()
        finality = "Change saved."
    else:
        finality = "Change not saved."
    conn.close()
    return finality