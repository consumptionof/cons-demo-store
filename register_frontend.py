from core_backend import get_result
from register_backend import *

active = 1
account = log_in()
fname = account[0]
lname = account[1]
uname = account[3]
print("Welcome, %s %s." % (fname, lname))
while active == 1:
    print("""Options: View transaction (1), locate by code (2),
    search for product (3), search for coupon (4), 
    search for customer by phone number (5), void last (6),
    void specific entry (7), finish transaction (8),
    lock register (9), sign off (10),
    manager actions (11)""")
    options = range(1, 12, 1)
    choice = get_result("Enter your choice: ", options)
    if choice in options:
        if choice == 1:
            view_transaction(uname)         # This function returns program data,
        elif choice == 2:                   # but prints information about the transaction,
            print(locate_by_code(uname))    # so no need to print it.
        elif choice == 3:
            print(search_product(uname))
        elif choice == 4:
            print(search_coupon(uname))
        elif choice == 5:
            print(search_card_by_phone(uname))
        elif choice == 6:
            print(void_last(uname))
        elif choice == 7:
            print(void(uname))
        elif choice == 8:
            print(payment(uname))
        elif choice == 9:
            unlock(uname)   # Just loops until the correct passcode
        elif choice == 11:  # is provided, so no need to print this either.
            manager = 1
            while manager == 1:
                manager_options = [1, 2, 3, 4]
                print("""Manager actions: Void transaction (1), suspend transaction (2),
                retrieve transaction (3). Or (4) to return.""")
                manager_choice = get_result("Enter your choice: ", manager_options)
                if manager_choice in manager_options:
                    if manager_choice == 1:
                        print(void_transaction(uname))  
                    elif manager_choice == 2:           
                        print(suspend_transaction(uname))
                    elif manager_choice == 3:
                        print(retrieve_transaction(uname))
                    else:
                        manager = 0
                else:
                    print("Invalid command.")
        else:                               
            active = 0
            print("Exiting.")
    else:
        print("Invalid command.")
    
    