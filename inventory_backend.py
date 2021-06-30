import sqlite3
import dateutil.parser as parser
from datetime import datetime, timedelta

def get_true(request):
    iter = 0
    result = 2
    while iter < 3:
        digit = input(request).lower()
        if digit == "no" or digit == "n" or digit == "0":
            result = 0
            iter = 3
        elif digit == "yes" or digit == "ye" or digit == "y" or digit == "1":
            result = 1
            iter = 3
        else:
            print("Invalid input.")
            iter = iter + 1
    return result

def get_result(request, *argv):
    iter = 0
    result = "wrong"
    while iter < 3:
        digit = input(request)
        if digit.isnumeric():
            digit = int(digit)
        for arg in argv:
            if digit == arg:
                result = digit
                iter = 3
        if result != digit:
            print("Invalid input.")
            iter = iter + 1
    return result


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
                print("The entry appears to already exist in coupon:")
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

def check_numeric(request):
    iter = 0
    result = "not_numeric"
    while iter < 3:
        digit = input(request)
        if not digit.isnumeric():
            print("Please enter a number.")
            iter = iter + 1
        else:
            result = digit
            iter = 3
    return result

def view(search, table):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    if table == "stock":
        if search.isnumeric():
            cur.execute("SELECT * FROM stock WHERE code = ?", (search,))
        elif search:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM stock WHERE name LIKE ? COLLATE NOCASE", (search,))
        else:
            cur.execute("SELECT * FROM stock")
    elif table == "coupons":
        if search.isnumeric():
            cur.execute("SELECT * FROM coupons WHERE code = ?", (search,))
        elif search:
            search = "%"+search+"%"
            cur.execute("SELECT * FROM coupons WHERE name LIKE ? COLLATE NOCASE", (search,))
        else:
            cur.execute("SELECT * FROM coupons")
    elif table == "cards":
        if search.isnumeric():
            search0 = input("Is this a phone number, or a card ID? ").lower()
            if search0 == "phone" or "phone number":
                cur.execute("SELECT * FROM cards WHERE phone = ?", (search,))
            elif search0 == "card id" or search0 == "id":
                cur.execute("SELECT * FROM cards WHERE id = ?", (search,))
        elif search:
            search = "%"+search+"%"
            search0 = input("Is this a first name or last name?").lower()
            if search0 == "first name" or search0 == "first" or search0 == "firstname":
                cur.execute("SELECT * FROM cards WHERE fname LIKE ? COLLATE NOCASE", (search,))
            elif search0 == "last name" or search0 == "last" or search0 == "lastname":
                cur.execute("SELECT * FROM cards WHERE fname LIKE ? COLLATE NOCASE", (search,))
        else:
            cur.execute("SELECT * FROM cards")
    rows = cur.fetchall()
    conn.close()
    return rows

def insert_coupon():
    name = input("What is the name of the coupon? ")
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("SELECT MAX(id2) FROM coupons")
    precode = cur.fetchall()
    conn.close()
    if precode[0] == (None,):
        precode = 0
    code = precode + 6000000001
    print("Auto-generated coupon code is %s" % code)
    icode = input("What is the item code affected by the coupon? ")
    disctype = get_result("Is this coupon a fixed discount (1), a percent off(2), or a new price (3)?  ",1,2,3)
    if disctype == "wrong":
        return "Invalid discount type."
    discval = input("What is the coupon's value? ")
    minquant = input("How many items are needed for the coupon? (Default is 0.01) ")
    if minquant == "":
        minquant = 0.01
    maxquant = input("What is the maximum number of times this coupon can be applied? (Default is infinite) ")
    if (maxquant.isnumeric() == False) or not maxquant:
        maxquant = 0
    doubled = get_true("Should the coupon be doubled? ")
    disccard = get_true("Is this coupon exclusive to rewards card members? ")
    if disccard == 1:
        points = input("What is the reward point cost for this coupon? (Default is 0) ")
        if (points.isnull()) or (points.isnumeric() == False):
            points = 0
    else:
        print("There will be no reward point cost for this coupon.")
        points = 0
    predate = input("What is the date at which this coupon should expire? (Default is 30 days in the future) ")
    if not predate:
        td = datetime.now()
        dt = timedelta(days=30)
        procdate = td + dt
    else:
        procdate = parser.parse(predate)
    expdate = procdate.isoformat()
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
    phone = check_numeric("What is the customer's phone number? (Include the area code.) ")
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("SELECT MAX(id3) FROM cards")
    precode = cur.fetchall()
    if precode[0] == (None,):
        precode = 0
    code = precode + 5000000001
    print("Automatically generated customer code is %s" % code)
    points = input("How many rewards points should the customer start with? (Default is 0)")
    if not points.isnumeric() or not points:
        points = 0
    conn.execute("INSERT INTO cards VALUES (NULL,?,?,?,?,?)",(fname,lname,phone,code,points))
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
    weigh = get_true("Should this item be sold by weight? Yes or No: ")
    if weigh == 2:
        return "Invalid weight entry."
    quan = check_numeric("How many of the product do you have? ")
    low_quan = check_numeric("How much/many of the product should be considered low stock? ")
    restock = get_true("Do you want to restock this item? ")
    if restock == 2:
        return "Invalid restock entry."
    if weigh == 1:
        print("The cashier will be asked to weigh this item.")
        spec_quant = 1
    else:
        spec_quant = get_true("Do you want the cashier to specify a quantity of this item? ")
        if spec_quant == 2:
            return "Invalid quantity specification entry."
    price = check_numeric("How much will this item cost, by each or by weight? ")
    tax = get_true("Is this item subject to sales tax? ")
    if tax == 2:
        return "Invalid sales tax entry."
    ebt = get_true("Is this item available to puchase with food stamps? ")
    if ebt == 2:
        return "Invalid food stamps entry."
    re_points = get_true("Does purchasing this item count towards rewards points? ")
    if re_points == 2:
        return "Invalid rewards point entry."
    age = input("What is the minimum age to purchase this item? Default is 0: ")
    if age == None or age.isnumeric() == False:
        age = 0
    disc_price = input("What should the rewards card price be? Default is same as regular price: ")
    if disc_price == None:
        disc_price = price
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO stock VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (name,code,weigh,quan,low_quan,restock,spec_quant,price,tax,ebt,re_points,age,disc_price))
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
        Store card discounted price: {}""".format(name, code, weigh, quan, low_quan, restock, spec_quant, price, tax, ebt, re_points, age, disc_price))

print("What do you want to do?")
command = input("Available: view, insert ").lower()
if command == "view":
    command0 = input("What table would you like to view (coupon, cards, or stock)? ")
    if command0 == "coupon" or command0 == "coupons":
        print(view(input("What coupon would you like to view? (Blank for all) "),"coupons"))
    elif command0 == "products" or command0 == "product" or command0 == "stock":
        print(view(input("What item would you like to search for? (Blank for all) "),"stock"))
    elif command0 == "cards" or command0 == "card" or command0 == "customer" or command0 == "customers":
        print(view(input("What customer would you like to search for? (Blank for all) "),"cards"))
    else:
        print("Invalid command.")
elif command == "insert":
    command0 = input("coupon, customer, or product? ").lower()
    if command0 == "coupon":
        print(insert_coupon())
    elif command0 == "customer":
        print(insert_customer())
    elif command0 == "product":
        print(insert_product())
    else:
        print("Invalid command.")
else:
    print("Sorry, that command doesn't exist (yet).")