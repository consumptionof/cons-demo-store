from core_backend import get_result
from register_backend import *

active = 1
account = login()
fname = account[0]
lname = account[1]
uname = account[3]
"""
options_dict = {
    1: view_transaction(uname),
    2: locate_by_code(uname),
    3: search_product(uname),
    4: search_coupon(uname),
    5: search_card_by_phone(uname),
    6: void_last(uname),
    7: void(uname),
    8: payment(uname),
    9: unlock(uname)
}
"""
print("Welcome, %s %s." % (fname, lname))
while active == 1:
    print("""Options: View transaction (1), locate by code (2),
    search for product (3), search for coupon (4), 
    search for customer by phone number (5), void last (6),
    void specific entry (7), finish transaction (8),
    lock register (9), sign off (10)""")
    options = range(1, 11, 1)
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
            unlock(uname)               # Just loops until the correct passcode
        else:                           # is provided, so no need to print this either.
            active = 0
            print("Exiting.")
    else:
        print("Invalid command.")
    
    