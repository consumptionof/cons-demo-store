import sqlite3
from sqlite3.dbapi2 import Cursor
import dateutil.parser as parser
from datetime import datetime, timedelta
import re

def get_true(request, default):
    iter = 0
    result = 2
    while iter < 3:
        digit = input(request).lower()
        if digit:
            if digit == "no" or digit == "n" or digit == "0":
                result = 0
                iter = 3
            elif digit == "yes" or digit == "ye" or digit == "y" or digit == "1":
                result = 1
                iter = 3
            else:
                print("Invalid input.")
                iter = iter + 1
        elif not digit and (default == 0 or default == 1):
            print("Using default...")
            result = default
            iter = 3
        else:
            print("Invalid input.")
            iter = iter + 1
    if result == 2:
        print("Using default...")
        result = default
    return result

def get_result(request, possibs):
    iter = 0
    result = "wrong"
    while iter < 3:
        digit = input(request)
        if digit.isnumeric():
            digit = int(digit)
        if digit in possibs:
            result = digit
            iter = 3
        if result != digit:
            print("Invalid input.")
            iter = iter + 1
    return result

def generate_code(ttype):
    dupe = 1
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    if ttype == "coupons":
        cur.execute("SELECT MAX(code) FROM coupons")
    elif ttype == "cards":
        cur.execute("SELECT MAX(code) FROM cards")
    elif ttype == "stock":
        cur.execute("SELECT MAX(code) FROM stock")
    else:
        return "invalid_table"
    maxcode = cur.fetchall()        # This returns a list with a single tuple,
    maxcode = maxcode[0]            # which contains a single number. This [0]
    maxcode = int(maxcode[0])       # business is extracting that one number.
    maxcode = maxcode + 1           # + 1 saves it from running that loop more than needed.
    while dupe == 1:
        cur.execute("SELECT code FROM coupons WHERE code = ?", (maxcode,))
        coupon_code = cur.fetchall()
        cur.execute("SELECT code FROM cards WHERE code = ?", (maxcode,))
        card_code = cur.fetchall()
        cur.execute("SELECT code FROM stock WHERE code = ?", (maxcode,))
        stock_code = cur.fetchall()
        if coupon_code or card_code or stock_code:
            maxcode = maxcode + 1
        else:
            dupe = 0
    conn.close()
    return maxcode

def stop_dupe(request, table, column):
    iter = 0
    result = "wr9ong" # This is a value that should never be in any of the tables.
    conn = sqlite3.connect("store.db") # If it is, something has gone terribly wrong.
    cur = conn.cursor()
    while iter < 3:
        digit = input(request)
        if digit == "":
            print("Please enter a value.")
            iter = iter + 1
            result = "no_result"
        else:
            if table == "coupon":
                cur.execute("SELECT * FROM coupon WHERE ? LIKE ?", (column, digit))
            elif table == "cards":
                cur.execute("SELECT * FROM cards WHERE ? LIKE ?", (column, digit))
            elif table == "stock":
                cur.execute("SELECT * FROM stock WHERE ? LIKE ?", (column, digit))
            else:
                return "table_not_exists"
            exists = cur.fetchall()
            if exists:
                print("The value %s already exists in table %s, column %s." % (digit,table,column))
                iter = iter + 1
                result = "item_exists"
            else:
                result = digit
                iter = 3
            conn.close()
        return result

def check_phone():
    iter = 0            # This function is necessary because it doesn't matter
    result = "exists"   # if a phone number conflicts with a code. They're completely separate.
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    while iter < 3: # Doesn't need an input to be specified; it only checks for one thing.
        pnumber = input("What is the customer's phone number? (Include the area code.) ")
        pnumber = re.sub("-","",pnumber)
        if pnumber.isnumeric():
            cur.execute("SELECT * FROM cards WHERE phone = ?", (pnumber,))
            phone_exists = cur.fetchall()
            if phone_exists:
                print("This phone number is already in use:\n%s" % phone_exists)
                iter = iter + 1
            else:
                result = pnumber
                iter = 3
        else:
            print("Please enter a number, with no other characters.")
            iter = iter + 1
    conn.close()
    return result

def check_codes(request):
    iter = 0
    result = "wr9ong" # This is a value that should never be a code.
    conn = sqlite3.connect("store.db") # If it is, something has gone terribly wrong.
    cur = conn.cursor()
    while iter < 3:
        digit = input(request)
        if digit == "":
            print("Please enter a code number.")
            iter = iter + 1
            result = "no_result"
        elif digit.isnumeric() == False:
            print("Codes must be numeric. Please enter a number.")
            iter = iter + 1
            result = "not_numeric"
        else:
            cur.execute("SELECT * FROM coupons WHERE code LIKE ?", (digit,))
            coupon_exists = cur.fetchall()
            cur.execute("SELECT * FROM cards WHERE code LIKE ?", (digit,))
            card_exists = cur.fetchall()
            cur.execute("SELECT * FROM stock WHERE code LIKE ?", (digit,))
            stock_exists = cur.fetchall()
            if coupon_exists:
                print("The entry appears to already exist in coupons:")
                print(coupon_exists)
                result = "exists"
                iter = iter + 1
            elif card_exists:
                print("The entry appears to already exist in cards:")
                print(card_exists)
                result = "exists"
                iter = iter + 1
            elif stock_exists:
                print("The entry appears to already exist in stock:")
                print(stock_exists)
                result = "exists"
                iter = iter + 1
            else:
                result = digit
                iter = 3
    conn.close()
    return result

def check_numeric(request,cannull,numtyp):
    iter = 0
    result = "not_numeric"
    while iter < 3:
        digit = input(request)
        if not digit and cannull == True:
            result = digit
            iter = 3
        else:
            try:           
                if numtyp == "float":
                    digit = float(digit)
                else: # Hopefully the only other value is "int".
                    digit = int(digit)
            except ValueError:
                print("Please enter a number.")
                iter = iter + 1
            else:
                result = digit
                iter = 3
    if not result or (result == "not_numeric" and cannull == True):
        print("Using default value...")
    return result

def view(search, table):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    numeric_search = False # Please do not put a table into this function.
    try: # Is this a string that can be converted into a number?
        numeric_search = search.isnumeric()
    except AttributeError: # No? Then is it an integer? If not, we'll look for a name.
        numeric_search = isinstance(search, int)
    if table == "stock":
        if numeric_search:
            cur.execute("SELECT * FROM stock WHERE code = ?", (search,))
        elif search:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM stock WHERE name LIKE ? COLLATE NOCASE", (search,))
        else:
            cur.execute("SELECT * FROM stock")
    elif table == "coupons":
        if numeric_search:
            search0 = get_result("Is this a code for a coupon (1), or for the affected item (2)? ", [1,2])
            if search0 == 1:
                cur.execute("SELECT * FROM coupons WHERE code = ?", (search,))
            elif search0 == 2:
                cur.execute("SELECT * FROM coupons WHERE item_code = ?", (search,))
            else:
                return search0
        elif search:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM coupons WHERE name LIKE ? COLLATE NOCASE", (search,))
        else:
            cur.execute("SELECT * FROM coupons")
    elif table == "cards":
        if numeric_search:
            search0 = get_result("Is this a phone number (1), or a card ID (2)? ", [1,2])
            if search0 == 1:
                cur.execute("SELECT * FROM cards WHERE phone = ?", (search,))
            elif search0 == 2:
                cur.execute("SELECT * FROM cards WHERE id = ?", (search,))
            else:
                return search0
        elif search:
            search = "%"+search+"%"
            search0 = get_result("Is this a first name (1) or last name (2)? ", [1,2])
            if search0 == 1:
                cur.execute("SELECT * FROM cards WHERE fname LIKE ? COLLATE NOCASE", (search,))
            elif search0 == 2:
                cur.execute("SELECT * FROM cards WHERE fname LIKE ? COLLATE NOCASE", (search,))
            else:
                return search0
        else:
            cur.execute("SELECT * FROM cards")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        search = re.sub("%","",search)
        rows = 'No results found for "%s".' % search
    return rows

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
    Coupon by each/weight (1), percent off (2), or new price (3): {}
    Minimum items for coupon: {}
    Maximum applications of this coupon: {}
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
    points = input("How many rewards points should the customer start with? (Default is 0) ", True, "int")
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
    if weigh == 2:
        return "Invalid weight entry."
    quan = check_numeric("How much/many of the product do you have? ", False, "float")
    if quan == "not_numeric":
        return "Invalid item quantity."
    low_quan = check_numeric("How much/many of the product should be considered low stock? ", False, "float")
    if low_quan == "not_numeric":
        return "Invalid low quantity value."
    restock = get_true("Do you want to restock this item? (Default is yes) ", 1)
    if restock == 2:
        return "Invalid restock entry."
    if weigh == 1:
        print("The cashier will be asked to weigh this item.")
        spec_quant = 1
    else:
        spec_quant = get_true("Do you want the cashier to specify a quantity of this item? (Default is no)", 0)
        if spec_quant == 2:
            return "Invalid quantity specification entry."
    price = check_numeric("How much will this item cost, by each or by weight? ", False, "float")
    if check_numeric == "not_numeric":
        return "Invalid price entry."
    tax = get_true("Is this item subject to sales tax? (Default is no) ", 0)
    if tax == 2:
        return "Invalid sales tax entry."
    ebt = get_true("Is this item available to puchase with food stamps? (Default is no) ", 0)
    if ebt == 2:
        return "Invalid food stamps entry."
    re_points = get_true("Does purchasing this item count towards rewards points? (Default is yes) ", 1)
    if re_points == 2:
        return "Invalid rewards point entry."
    age = check_numeric("What is the minimum age to purchase this item? Default is 0: ", True, "int")
    if not age or age == "not_numeric" :
        age = 0
    disc_price = check_numeric("What should the rewards card price be? Default is same as regular price: ", True, "float")
    if not disc_price or disc_price == "not_numeric":
        disc_price = price
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO stock VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (name,code,weigh,quan,low_quan,restock,
                spec_quant,price,tax,ebt,re_points,age,disc_price))
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
        Store card discounted price: {}""".format(name, code, weigh, quan, low_quan,
        restock, spec_quant, price, tax, ebt, re_points, age, disc_price))

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
    options = [*range(1, 11, 1)]
    var_to_use = get_result("Enter your selection: ", options)
    if not isinstance(var_to_use, int):
        return var_to_use

    if var_to_use == 1:             # I would just use one cur.execute, but the name is vulnerable to SQL injection.
        cur.execute("SELECT name FROM coupons WHERE id2 = ?", (row_id,)) # Plus, all these different variables need to be treated differently.
        old_val = cur.fetchone()    # Setting up for a comparison at the end.
        new_val = input("What is the new name of the coupon? ")
        cur.execute("UPDATE coupons SET name = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 2:
        cur.execute("SELECT code FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_codes("What is the new coupon code? ")
        if new_val == "exists":
            return "Invalid coupon code."
        cur.execute("UPDATE coupons SET code = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 3:
        cur.execute("SELECT item_code FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What item code should the coupon affect? ", False, "int")
        if new_val == "not_numeric":
            return "Invalid item code."
        cur.execute("UPDATE coupons SET item_code = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 4:
        cur.execute("SELECT each_weigh FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_result("Is this coupon a fixed discount (1), a percent off(2), or a new price (3)? ",(1,2,3))
        if new_val == "Invalid input.":
            return new_val
        cur.execute("UPDATE coupons SET each_weigh = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 5:
        cur.execute("SELECT value FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the new coupon value? ", False, "float")
        if new_val == "not_numeric":
            return "Invalid coupon value."
        cur.execute("UPDATE coupons SET value = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 6:
        cur.execute("SELECT min FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the new minimum items for the coupon? (Default is 0.01) ", True, "float")
        if new_val == "not_numeric" or not new_val:
            new_val = 0.01
        cur.execute("UPDATE coupons SET min = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 7:
        cur.execute("SELECT max FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the maximum number of times this coupon may be applied? (Default is infinite) ", False, "float")
        if new_val == "not_numeric" or not new_val:
            new_val = "0"
        cur.execute("UPDATE coupons SET max = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 8:
        cur.execute("SELECT doubled FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Should this coupon be doubled? (Default is no) ", 0)
        if new_val == 2:
            return "Invalid coupon doubling."
        cur.execute("UPDATE coupons SET doubled = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 9:
        cur.execute("SELECT disc_card FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = get_true("Should this coupon be exclusive to rewards card members? (Default is no) ", 0)
        if new_val == 2:
            return "Invalid rewards cselected_roward exclusivity."
        cur.execute("UPDATE coupons SET disc_card = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 10:
        cur.execute("SELECT expire FROM coupons WHERE id2 = ?", (row_id,))
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
        cur.execute("UPDATE coupons SET expire = ? WHERE id2 = ?", (new_val, row_id))
    elif var_to_use == 11:
        cur.execute("SELECT re_cost FROM coupons WHERE id2 = ?", (row_id,))
        old_val = cur.fetchone()
        new_val = check_numeric("What is the rewards point cost of this coupon? (Default is none) ", True, "int")
        if new_val == "not_numeric" or not new_val:
            new_val = 0
        cur.execute("UPDATE coupons SET re_cost = ? WHERE id2 = ?", (new_val, row_id))
    else:
        return "Please choose an entry to change."
    old_val = old_val[0]
    print("""Old value: {}
    New value: {}""".format(old_val,new_val))
    decision = get_true("Are you sure you want to make this change? ", 0)
    if decision == 1:
        conn.commit()
        finality = "Change saved."
    else:
        finality = "Change not saved."
    conn.close()
    return finality

def update_customer():
    return "This function is under construction. Please check back later."

def update_stock():
    return "This function is under construction. Please check back later."

print("What do you want to do?")
command = input("Available: view, insert ").lower()
if command == "view":
    command0 = input("What table would you like to view (coupon, cards, or stock)? ")
    if command0 == "coupon" or command0 == "coupons":
        prompt = input("What coupon would you like to view? (Blank for all) ")
        print(view(prompt,"coupons"))
    elif command0 == "products" or command0 == "product" or command0 == "stock":
        prompt = input("What item would you like to search for? (Blank for all) ")
        print(view(prompt,"stock"))
    elif command0 == "cards" or command0 == "card" or command0 == "customer" or command0 == "customers":
        prompt = input("What customer would you like to search for? (Blank for all) ")
        print(view(prompt,"cards"))
    else:
        print("Invalid command.")
elif command == "insert":
    command0 = input("coupon, customer, or product? ").lower()
    if command0 == "coupon":
        print(insert_coupon())
    elif command0 == "customer" or command0 == "card":
        print(insert_customer())
    elif command0 == "product" or command0 == "stock":
        print(insert_product())
    else:
        print("Invalid command.")
else:
    print("Sorry, that command doesn't exist (yet).")