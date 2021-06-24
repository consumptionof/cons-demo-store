import sqlite3

def get_true(request):
    iter = 0
    result = 2
    while iter < 3:
        digit = input(request).lower()
        if digit == "yes" or digit == "y" or digit == "1":
            result = 1
            iter = 3
        elif digit == "no" or digit == "n" or digit == "0":
            result = 0
            iter = 3
        else:
            print("Invalid input.")
            iter = iter + 1
    return (result)

def view(search):
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    if search.isnumeric():
        cur.execute("""SELECT *
        FROM stock
        WHERE code = ?
        """, (search,))
    elif search:
        search = "%"+search+"%"
        cur.execute("""SELECT *
        FROM stock
        WHERE name LIKE ?
        COLLATE NOCASE
        """, (search, ))
    else:
        cur.execute("SELECT * FROM stock")
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

def insert_coupon():
    name = input("What is the name of the coupon? ")
    code = input("What is the coupon's code? ")
    icode = input("What is the item code affected by the coupon? ")
    weighorcent = input("Is this coupon per item/by weight, or a fixed percent? (Default is each) ")
    minquant = input("How many items are needed for the coupon? (Leave blank for 0.01) ")
    if minquant == "":
        minquant = 0.01
    
    return "Todo, sorry!"

def insert_customer():
    return "Todo, sorry!"

def insert_product():
    name = input("What is the product's name? ")
    code = input("What is the product's code number or PLU? ")
    request = "Should this item be sold by weight? Yes or No: "
    weigh = get_true(request)
    if weigh == 2:
        return "Invalid store entry."
    quan = input("How many of the product do you have? ")
    low_quan = input("How much/many of the product should be considered low stock? ")
    request = "Do you want to restock this item? "
    restock = get_true(request)
    if restock == 2:
        return "Invalid store entry."
    if weigh == 1:
        print("The cashier will be asked to weigh this item.")
        spec_quant = 1
    else:
        request = "Do you want the cashier to specify a quantity of this item? "
        spec_quant = get_true(request)
        if spec_quant == 2:
            return "Invalid store entry."
    price = input("How much will this item cost, by each or by weight? ")
    request = "Is this item subject to sales tax? "
    tax = get_true(request)
    if tax == 2:
        return "Invalid store entry."
    request = "Is this item available to puchase with food stamps? "
    ebt = get_true(request)
    if ebt == 2:
        return "Invalid store entry."
    request = "Does purchasing this item count towards rewards points? "
    re_points = get_true(request)
    if re_points == 2:
        return "Invalid store entry."
    age = input("What is the minimum age to purchase this item? Default is 0: ")
    if age == None or age.isnumeric() == False:
        age = 0
    disc_price = input("What should the rewards card price be? Default is same as regular price: ")
    if disc_price == None:
        disc_price = price
    conn = sqlite3.connect("store.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO stock VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)", (name,code,weigh,quan,low_quan,restock,spec_quant,price,tax,ebt,re_points,age,disc_price))
    conn.commit()
    conn.close()
    return ("""Inserted product.
        Name: {}
        Code number or PLU: {}
        Sold by weight: {}
        Quantity in stock: {}
        Low stock threshold: {}
        Should it be res or disc_price.isnumeric() == Falsetocked: {}
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
    print(view(input("What code would you like to search for? (Blank for all) ")))
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