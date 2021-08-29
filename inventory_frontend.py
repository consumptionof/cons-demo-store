from inventory_backend import *

incomplete = 1

account = log_in()
fname = account[0]
lname = account[1]
actype = account[2]
if actype == 1:
    print("You need to be a managerto use the backend program.")
else:
    print("Welcome, %s %s." % (fname, lname))
    while incomplete == 1:
        command = get_result("Would you like to work with products (1), coupons (2), customers (3), or employees (4)? Or would you like to exit (5)? ", [1, 2, 3, 4 ,5])
        if command == 1:
            products = 1
            while products == 1:
                command0 = get_result("Would you like to view (1), add (2), or update (3) a product? Or would you like to go back (4)? ", [1, 2, 3, 4])
                if command0 == 1:
                    prompt = input("What product would you like to view? Enter a code or name, or blank for all: ")
                    print(view(prompt, "stock"))
                elif command0 == 2:
                    print(insert_product())
                elif command0 == 3:
                    print(update_stock())
                elif command0 == 4:
                    products = 0
                else:
                    print("Invalid command.")
        elif command == 2:
            coupons = 1
            while coupons == 1:
                command0 = get_result("Would you like to view (1), add (2), or update (3) a coupon? Or would you like to go back (4)? ", [1, 2, 3, 4])
                if command0 == 1:
                    prompt = input("What coupon would you like to view? Enter a code or name, or blank for all: ")
                    print(view(prompt, "coupons"))
                elif command0 == 2:
                    print(insert_coupon())
                elif command0 == 3:
                    print(update_coupon())
                elif command0 == 4:
                    coupons = 0
                else:
                    print("Invalid command.")
        elif command == 3:
            cards = 1
            while cards == 1:
                command0 = get_result("Would you like to view (1), add (2), or update (3) a customer? Or would you like to go back (4)? ", [1, 2, 3, 4])
                if command0 == 1:
                    prompt = input("What customer would you like to view? Enter a code or name, or blank for all: ")
                    print(view(prompt, "cards"))
                elif command0 == 2:
                    print(insert_customer())
                elif command0 == 3:
                    print(update_customer())
                elif command0 == 4:
                    cards = 0
                else:
                    print("Invalid command.")
        elif command == 4:
            employees = 1
            while employees == 1:
                command0 = get_result("Would you like to view (1), add (2), or update (3) an employee? Or would you like to go back? (4)? ", [1, 2, 3, 4])
                if command0 == 1:
                    prompt = input("What employee would you like to view? Enter a login code or name, or blank for all: ")
                    print(view(prompt, "employees"))
                elif command0 == 2:
                    print(insert_employee())
                elif command0 == 3:
                    print(update_employee())
                elif command0 == 4:
                    employees = 0
                else:
                    print("Invalid command.")
        elif command == 5:
            incomplete = 0
        else:
            print("Invalid command.")
    print("Exiting program.")