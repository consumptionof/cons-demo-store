# Overview

This is a simple grocery store program
running on Python 3 and using SQLite.

The store will feature products sold both by weight
and per each item, discounts automatically applied
to products, coupon codes, and rewards card
membership.

## What's working

Currently, the following are the functioning parts of the program:
- The initialization script, which creates an empty
database template with all the requisite information.
- Adding items to the stock table.
- Adding coupons to the coupons table.
- Searching for products, coupons, and rewards card members.


The products table, part of the store database,
currently tracks the following:
- An item ID generated by the program.
- The name of the product.
- The code the cashier types in for the product.
  This can take the form of produce PLU numbers
  or the barcode of the item.
- The amount of an item available.
  This is tracked either per item or by weight.
- An available product threshold at which the manager
  is alerted of low stock.
- Whether or not an item will be restocked.
  If not, the manager will not be warned of low stock.
- Whether or not the cashier should manually type in
  the quantity of the product requested.
  This is useful so that the cashier can easily enter,
  for example, eight lemons without having to manually
  specify regular, one-off products as just one every time.
- The price of the product. The program will automatically
  determine whether this price is per each item or by weight.
- Whether or not the item is subject to sales tax.
- Whether or not the item is purchasable with food stamps.
- Whether or not purchasing the item will count towards
  earned rewards points.
- The minimum age the customer must be to purchase the item.
  If set to 0, the register will not ask for a birth date.
- The discounted price offered to rewards card members.

The coupons table in the same database
currently tracks the following:
- An ID tracked by the program.
- The name of the coupon. Usually similar to
  the item it's discounting.
- A code auto-generated by the program that the
  cashier can manually enter.
- The item code affected by the coupon. If this item
  isn't present in the transaction, the coupon is unavailable.
- Whether a coupon is a fixed discount per pound/each (like $0.50),
  a percent off, or a new price.
- The value of the coupon.
- The minimum number of items required to get the coupon.
  For weighed items, this starts at 0.01.
  It's the same for items sold normally, but it should still
  work the same.
- The maximum number of times the coupon can be applied
  per transaction. 0 is the default, and means there is no limit.
- Whether or not the coupon should be doubled.
- Whether or not the coupon is exclusive to rewards card members.
- The expiration date of the coupon.
- The rewards point cost of the coupon.


## What's planned

- A manager GUI program that allows the manager to
  add and modify coupons, products, and rewards card members.
  In the inventory window, it will be able to add new products,
  update their inventory quantity, set discounts, 
  and mark items as no longer stocked.
  In the coupons window, it will be able to add coupons with
  values, item codes, and expiration dates.
  In the rewards member window, it will be able to register
  new customers with their name and phone number,
  and it will automatically generate a unique ID
  of the customer the register can look up.
  (The register will also be able to look up customers by phone number.)
- A cashier GUI program that simulates the sale of products by reading
  product, coupon, and rewards card membership data.
  It will (hopefully) do this without unnecessarily destroying
  any of the tables or data.
  The cashier program will also generate receipts as text files
  containing the total price of the order,
  how much the customer saved with automatic discounts and coupons,
  the rewards points earned during the transaction,
  the rewards points expended during the transaction,
  and the customer's total remaining rewards points.

## Why do you have so many functions?
  That's mostly for my own convenience. I hate when I mistype
  something and the program immediately dies over a typo,
  forcing me to retype everything I'd already entered
  up to that point. Or when I mistype something,
  the program doesn't recognize it, and something
  wrong is put into the database -- something I may not
  realize at the time, but will have to dig in and correct.
  I'll bet a lot of users in general feel that way, as well.
  So, as long as this is a CLI program, they will stay.
  Maybe when I take this to a GUI I'll be able to rework
  them to work with text entry fields.

### Version 0.013
- Added core_backend.py
  This file will house the essential functions like check_numeric
  and get_true for both the inventory and register backends.
- Added register_backend.py
  This will house the programs needed only for the register.
  For example, a register will need to add things to the
  transaction, while the inventory system has no use for such
  a thing.
- Added the store_data table during database creation
  For now, this table only holds the store name and the sales tax
  applicable to the current store.
- Added current_trans and current_trans_meta for use in transactions
  current_trans holds all the items and coupons requested by
  the customer, while current_trans_meta contains the cashier's
  name and ID, whether or not the discount card is in use,
  and the customer's birthdate.

### Version 0.012
- Added view_mech
  This is a new version of view intended mainly for the program
  itself to search for something. The old view is being kept
  as there isn't that much wrong with it. It is a little limited,
  and difficult to automate, so view_mech will fill that niche.
- Updated store.db
  Now, instead of the first columns being called "id1," "id2," etc.,
  they're all just "id." I don't know why I rolled with that for so long.
  But in any case, the program no longer uses "id1" or "id2" either.
- Added departments to the stock table
  This will make it easier to organize in the future, when the
  register will search for things by department.
  The initial.py script also includes the department column now.

### Version 0.011
- Added insert_employee
  You can now add employees to a table. This will store their
  basic information. For the moment, it only stores their name,
  account type, login, and passcode.
- Added update_employee
  This, like the other update functions, will allow you to
  change whatever variables you'd like about an employee.
  (Please do not change the last remaining manager account
  to a cashier account, otherwise you will no longer
  be able to update the inventory without manually changing 
  the account type in the database.)
- Added login
  This function asks for a login number and passcode.
  The inventory control will require a manager account to use
  from now on.
- Added inventory_frontend.py
  This program will let you use the primary functions
  in inventory_backend.py. I probably should have made
  this program way sooner, but you could say that about
  a lot of this program's features.
- The interface now has you select which type of data
  you'd like to view/update rather than asking
  what you want to do, then what you want to manipulate.
- view now searches for employees.
  Sidenote: Please do not name any of your employees anything
  containing "cashier"  or "manager", as this will break
  the view function.
- stop_dupe now checks for employee information.
- The inventory backend now requires getpass.
- initial.py now creates the employees table,
  and creates a manager account at setup.
- The interface now uses get_result instead of having
  keywords.

### Version 0.010
- view now actually searches for last names when specified.

- generate_code now uses fetchone instead of fetchall.
  This gives a tuple containing a single integer,
  rather than a list containing a tuple containing a single integer.

- Added update_customer
  This will allow the user to change anything about the customer's
  rewards program account without having to play with SQL.

### Version 0.09
- Updated update_coupon
  update_coupon now checks to see if the coupon value is greater
  than the original item's price. It will also check to see if
  the specified item code already has a coupon associated with it.

- All functions throughout the program no longer check if an
  incorrect value is returned from get_true, as get_true
  only returns 0 or 1 now.

- Updated insert_coupon so it checks whether or not coupons
  exist for a product.

- Added update_stock
  This function works very similarly to update_coupon, but
  for products.

### Version 0.08
- Updated view
  I'm going to try building the update_(things) functions
  around the view function. To that end, I've made it so that
  it'll properly detect if something is a number or not.
  For now, it'll only work with integers. Later on,
  once this script is worked into a GUI program,
  I might add the ability to search for prices.
  That doesn't seem very helpful at the moment.
  Furthermore, you can now search for the code of the item
  affected by coupons. This is a much more useful thing
  to search for than memorizing the exact number of 0s 
  to put after the 6 and before the main code.
  More generally, it now uses get_result instead of just
  depending on its own resolution.

- Updated check_numeric
  This function now expects an input specifying
  whether the expected result is an integer or a float.
  Don't ask why I was so resistant to the idea, I'm
  not really sure.
  It also states when the default value is being used,
  if one is being used.

- Added update_coupon
  This function will update existing entries in
  the coupons table. You can change any variable you wish.
  (If you change the entry so that a non-rewards card
  member can get a coupon, but assign it a rewards point
  value, it will probably break things. Please don't do that.)
  This is the first of the three update functions I'll be making.

- Updated get_true
  This function now automatically uses the provided default
  value if either no input is provided, or the input is wrong
  too many times.

### Version 0.07
- Updated get_true
  get_true can now accept default values.
  The default is either 0, 1, or 2.
  0 functions as False, 1 as True,
  and 2 as an error. 2 is returned either if the user
  entered nothing and no default value was intended,
  or if the user put in an incorrect input too many times.
  I've also updated the insert functions with this new function.

- Added check_phone
  This function just checks if a phone number exists.
  I would revise check_codes to look at phone numbers
  given a particular table name, but it would require me to 
  also change the function so it wouldn't return a float.
  IMO, it's easier to just use check_phone like this.

- Made it so that check_codes actually does something.
  It used to complete the function when iter < 3 was false,
  which, of course, was set to 0 at the very start of the function.
  Hopefully I don't have to do that anymore.
  (Maybe this sounds a bit degrading, but I figure it's okay,
  since I'm only degrading myself.)

  I've also started work on the update_coupon function.
  It's not nearly in working order yet, but I think
  I might be able to make it call view and use those results
  rather than rewriting a whole new "find entries in this table"
  function. I might do something with the many functions
  in the program, try to unify them a bit, but that
  will come later.

### Version 0.06
- Updated check_numeric
  In its original incarnation, check_numeric would just check
  to see if a value was numeric. It failed to do so in cases
  where the number has decimal numbers, like 1.5.
  Now, it will check to see if something can be converted
  to a float. If it can, it'll do so. If not, it'll tell
  the user so, ask for another input. Rinse and repeat,
  like the other "check" or "get" functions.
  In addition, it can also be told that it's okay if
  the user doesn't put anything in. This is necessary
  wherever the program has a defined default value
  or other system in place, like the number of rewards
  points a customer starts out with.

  I've updated insert_customer and insert_coupon
  with the new check_numeric function. insert_product
  will be updated soon.

- Added generate_code
  I realized that simply making an auto-generated code
  increment from the highest ID number would likely
  lead to conflicts in item codes. I kind of addressed this
  with check_codes and stop_dupe, but those would just
  stop the program in its tracks. This function will
  detect the largest value in a specified table,
  create one that's greater by 1 (say, 4000 to 4001),
  then checks all other tables for an identical code.
  If there is one, it'll increment the value by 1 again.
  It'll keep doing this until it gets a unique value,
  then return it to the previous function.

- Added some placeholder functions for updating products,
  customer rewards cards, and coupons.

### Version 0.05
First of all, I'm going to try to implement version numbers into
the program. That should make it easier to keep track of what
changes happened when. It appears that there have been four
commits before this one, so this version is being called 0.05.

This program uses many functions to determine the validity
of inputs. I've added one such function to detect if a value
is numeric in cases where it should be. I don't think it's
necessary to add one for detecting things that aren't numeric,
though. Plenty of products have numbers in their names, and in a
world where people specifically name their kids after 20th-century
dictators, can you really make any assumptions about people's names?
Off the tangent, the next step is to implement this function
in the database entry functions.