import sqlite3
import re
import getpass

chances = [*range(0, 3)]

def get_true(request, default):
    result = 2 # Please tell the user the default value.
    for i in chances:
        digit = input(request).lower()
        if digit:
            if digit == "no" or digit == "n" or digit == "0":
                result = 0
                break
            elif digit == "yes" or digit == "ye" or digit == "y" or digit == "1":
                result = 1
                break
            else:
                print("Invalid input.")
        elif not digit:
            print("Using default...")
            result = default
            break
        else:
            print("Invalid input.")
    if result == 2:
        print("Using default...")
        result = default
    return result

def get_result(request, possibs):   # possibs is a list or tuple.
    result = "wrong"                # I don't know what will happen if you
    for i in chances:               #put a dictionary there.
        digit = input(request)
        if digit.isnumeric():
            digit = int(digit)
        if digit in possibs:
            result = digit
            break
        if result != digit:
            print("Invalid input.")
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
    maxcode = cur.fetchone()        # This will give us a tuple with one entry.
    if not maxcode[0]:
        maxcode = 1
    else:
        maxcode = int(maxcode[0])       # This line extracts the entry and converts it to an int.
        maxcode += 1                    # + 1 saves it from running that loop more than needed.
    while dupe == 1:
        cur.execute("SELECT code FROM coupons WHERE code = ?", (maxcode,))
        coupon_code = cur.fetchone()
        cur.execute("SELECT code FROM cards WHERE code = ?", (maxcode,))
        card_code = cur.fetchone()
        cur.execute("SELECT code FROM stock WHERE code = ?", (maxcode,))
        stock_code = cur.fetchone()
        if coupon_code or card_code or stock_code:
            maxcode += 1
        else:
            if ttype == "coupons" and maxcode == 1:
                maxcode = maxcode + 6000000000
            elif ttype == "cards" and maxcode == 1:
                maxcode = maxcode + 5000000000
            dupe = 0
    conn.close()
    return maxcode

def stop_dupe(request, table, column):
    iter = 0
    result = "wr9ong" # This is a value that should never be in any of the tables.
    conn = sqlite3.connect("store.db") # If it is, something has gone terribly wrong.
    cur = conn.cursor()
    while iter == 0:
        digit = input(request)
        if digit == "":
            print("Please enter a value.")
            #iter = iter + 1
            result = "no_result"
        else:
            if table == "coupon":
                cur.execute("SELECT * FROM coupon WHERE ? LIKE ?", (column, digit))
            elif table == "cards":
                cur.execute("SELECT * FROM cards WHERE ? LIKE ?", (column, digit))
            elif table == "stock":
                cur.execute("SELECT * FROM stock WHERE ? LIKE ?", (column, digit))
            elif table == "employees":
                cur.execute("SELECT * FROM employees WHERE ? LIKE ?", (column, digit))
            else:
                return "table_not_exists"
            exists = cur.fetchall()
            if exists:
                print("The value %s already exists in table %s, column %s." % (digit,table,column))
                #iter = iter + 1
                result = "item_exists"
            else:
                result = digit
                iter = 1
            conn.close()
        return result

def check_phone():      # This function is necessary because it doesn't matter
    result = "exists"   # if a phone number conflicts with a code. They're completely separate.
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    for i in chances: # Doesn't need an input to be specified; it only checks for one thing.
        pnumber = input("What is the customer's phone number? (Include the area code.) ")
        pnumber = re.sub("-","",pnumber)
        if pnumber.isnumeric():
            cur.execute("SELECT * FROM cards WHERE phone = ?", (pnumber,))
            phone_exists = cur.fetchall()
            if phone_exists:
                print("This phone number is already in use:\n%s" % phone_exists)
            else:
                result = pnumber
                break
        else:
            print("Please enter a number, with no other characters.")
    conn.close()
    return result

def check_codes(request):
    result = "wr9ong"                  # This is a value that should never be a code.
    conn = sqlite3.connect("store.db") # If it is, something has gone terribly wrong.
    cur = conn.cursor()
    for i in chances:
        digit = input(request)
        if digit == "":
            print("Please enter a code number.")
            result = "no_result"
        elif digit.isnumeric() == False:
            print("Codes must be numeric. Please enter a number.")
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
            elif card_exists:
                print("The entry appears to already exist in cards:")
                print(card_exists)
                result = "exists"
            elif stock_exists:
                print("The entry appears to already exist in stock:")
                print(stock_exists)
                result = "exists"
            else:
                result = digit
                break
    conn.close()
    return result

def check_numeric(request,cannull,numtyp):
    result = "not_numeric"
    for i in chances:
        digit = input(request)
        if not digit and cannull == True:
            result = digit
            break
        else:
            try:           
                if numtyp == "float":
                    digit = float(digit)
                else: # Hopefully the only other value is "int".
                    digit = int(digit)
            except ValueError:
                print("Please enter a number.")
            else:
                result = digit
                break
    if not result or (result == "not_numeric" and cannull == True):
        print("Using default value...")
    return result

def log_in():
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    correct = 0
    uname = ""
    passcode = ""
    while correct == 0:
        while not uname:
            uname = input("Enter your login code: ")
            try:
                uname = int(uname)
            except ValueError:
                print("Please enter an integer.")
                uname = ""
        while not passcode:
            passcode = getpass.getpass("Enter your passcode: ")
            try:
                passcode = int(passcode)
            except ValueError:
                print("Please enter an integer.")
                passcode = ""
        cur.execute("SELECT passcode FROM employees WHERE login = ?", (uname,))
        check = cur.fetchone()
        if check:
            check = check[0] # Still have to extract that thing.
            if passcode == check:
                cur.execute("SELECT fname, lname, actype, login FROM employees WHERE login = ?", (uname,))
                info = cur.fetchall()
                info = info[0]
                return info
            else:
                uname = ""      # You need to do this, otherwise it'll just go
                passcode = ""   # "Incorrect password." forever.
                print("Incorrect password.")
        else:
            uname = ""
            passcode = ""
            print("User does not exist.")

def unlock(login):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    unlocked = False
    cur.execute("SELECT fname, passcode FROM employees WHERE login = ?", (login,))
    user_info = cur.fetchone()
    fname = user_info[0]
    passcode = user_info[1]
    while unlocked == False:
        attempt = getpass.getpass("Enter %s's passcode: " % fname)
        try:
            attempt = int(attempt)
        except ValueError:
            pass                # Passcodes can only be integers,
        if attempt == passcode: # and Python will freak out if you try to make a str == int,
            unlocked = True     # so this step is necessary for it to not crash.
        else:
            print("Incorrect passcode.")
    return True 

def sanitize(target):
    target = re.sub("drop table", "", target, flags = re.IGNORECASE)
    target = re.sub("delete", "", target, flags = re.IGNORECASE)
    target = re.sub(";", "", target)
    target = re.sub("--", "", target)
    return target

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
                cur.execute("SELECT * FROM cards WHERE lname LIKE ? COLLATE NOCASE", (search,))
            else:
                return search0
        else:
            cur.execute("SELECT * FROM cards")
    elif table == "employees":
        if numeric_search:
            search0 = get_result("Is this a type of account (1), a login code (2), or a passcode (3)? ", [1,2,3])
            if search0 == 1:
                cur.execute("SELECT * FROM employees WHERE actype = ?", (search,))
            elif search0 == 2:
                cur.execute("SELECT * FROM employees WHERE login = ?", (search,))
            elif search0 == 3:
                cur.execute("SELECT * FROM employees WHERE pass = ?", (search,))
            else:
                return search0
        elif search:
            if "cashier" in search:
                cur.execute("SELECT * FROM employees WHERE actype = 1")
            elif "manager" in search:
                cur.execute("SELECT * FROM employees WHERE actype = 2")
            else:
                search = "%"+search+"%"
                search0 = get_result("Is this a first name (1), or a last name(2)? ", [1,2])
                if search0 == 1:
                    cur.execute("SELECT * FROM employees WHERE fname LIKE ? COLLATE NOCASE", (search,))
                elif search0 == 2:
                    cur.execute("SELECT * FROM employees WHERE lname LIKE ? COLLATE NOCASE", (search,))
                else:
                    return search0
        else:
            cur.execute("SELECT * FROM employees")
    else:
        return "Invalid table. Please review the program and report to the developer."
    rows = cur.fetchall()
    conn.close()
    if not rows:
        search = re.sub("%","",search)
        rows = 'No results found for "%s".' % search
    return rows

def view_mech(search, table, column):   # This function is for when the program itself,
    conn = sqlite3.connect("store.db")  # rather than the user, needs to search for something.
    cur = conn.cursor()
    if table == "stock":            # I wish I knew a better way to do this. I can't use
        if column == 1:             # regular string substitution without opening up 
            search = "%"+search+"%" # the possibility of an injection attack.
            cur.execute("SELECT * FROM stock WHERE name LIKE ? COLLATE NOCASE", (search,))
        elif column == 2:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM stock WHERE code LIKE ?", (search,))
        elif column == 3:
            cur.execute("SELECT * FROM stock WHERE weigh = ?", (search,))
        elif column == 4:
            cur.execute("SELECT * FROM stock WHERE quan = ?", (search,))
        elif column == 5:
            cur.execute("SELECT * FROM stock WHERE low_quan = ?", (search,))
        elif column == 6:
            cur.execute("SELECT * FROM stock WHERE restock = ?", (search,))
        elif column == 7:
            cur.execute("SELECT * FROM stock WHERE spec_quant = ?", (search,))
        elif column == 8:
            cur.execute("SELECT * FROM stock WHERE price = ?", (search,))
        elif column == 9:
            cur.execute("SELECT * FROM stock WHERE tax = ?", (search,))
        elif column == 10:
            cur.execute("SELECT * FROM stock WHERE ebt = ?", (search,))
        elif column == 10:
            cur.execute("SELECT * FROM stock WHERE re_points = ?", (search,))
        elif column == 11:
            cur.execute("SELECT * FROM stock WHERE age = ?", (search,))
        elif column == 12:
            cur.execute("SELECT * FROM stock WHERE disc_price = ?", (search,))
        elif column == 13:
            cur.execute("SELECT * FROM stock WHERE department = ?", (search,))
        else:
            cur.execute("SELECT * FROM stock")
    elif table == "coupons":
        if column == 1:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM coupons WHERE name LIKE ? COLLATE NOCASE", (search,))
        elif column == 2:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM coupons WHERE code LIKE ?", (search,))
        elif column == 3:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM coupons WHERE item_code LIKE ?", (search,))
        elif column == 4:
            cur.execute("SELECT * FROM coupons WHERE each_weigh = ?", (search,))
        elif column == 5:
            cur.execute("SELECT * FROM coupons WHERE value = ?", (search,))
        elif column == 6:
            cur.execute("SELECT * FROM coupons WHERE min = ?", (search,))
        elif column == 7:
            cur.execute("SELECT * FROM coupons WHERE max = ?", (search,))
        elif column == 8:
            cur.execute("SELECT * FROM coupons WHERE doubled = ?", (search,))
        elif column == 9:
            cur.execute("SELECT * FROM coupons WHERE disc_card = ?", (search,))
        elif column == 10:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM coupons WHERE expire LIKE ?", (search,))
        else:
            cur.execute("SELECT * FROM coupons")
    elif table == "cards":
        if column == 1:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM cards WHERE fname LIKE ? COLLATE NOCASE", (search,))
        elif column == 2:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM cards WHERE lname LIKE ? COLLATE NOCASE", (search,))
        elif column == 3:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM cards WHERE phone LIKE ?", (search,))
        elif column == 4:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM cards WHERE code LIKE ?", (search,))
        elif column == 5:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM cards WHERE points LIKE ?", (search,))
        else:
            cur.execute("SELECT * FROM cards")
    elif table == "employees":
        if column == 1:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM employees WHERE fname LIKE ? COLLATE NOCASE", (search,))
        elif column == 2:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM employees WHERE lname LIKE ? COLLATE NOCASE", (search,))
        elif column == 3:
            cur.execute("SELECT * FROM employees WHERE actype = ?", (search,))
        elif column == 4:
            cur.execute("SELECT * FROM employees WHERE login = ?", (search,))
        elif column == 5:
            cur.execute("SELECT * FROM employees WHERE passcode = ?", (search,))
        else:
            cur.execute("SELECT * FROM employees WHERE * = ?", (search,))
    else:
        return "Invalid table. Please review the program and report to the developer."
    rows = cur.fetchall()
    conn.close()
    if not rows:
        if isinstance(search, str):
            search = re.sub("%","",search)
        rows = 'No results found for "%s".' % search
    return rows