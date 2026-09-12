"""
CIT 1203 - PROGRAMMING FUNDAMENTALS
GROUP COURSEWORK - OPTION 2
Campus Food Delivery and Order Management System

Group work division:
    a) Menu setup                        - Harshil
    b) Order taking                      - Harshil
    c) Rider assignment & status track   - Oscar
    d) Sales and reporting               - Churchill
    e) File persistence                  - Alvin
    f) Menu-driven driver programme      - Alvin

This program lets a canteen attendant take customer orders, assign a
delivery rider, track the order status, see sales reports and keep the
order records saved in a text file so nothing is lost when the program
is closed and reopened.
"""

import os

# ------------------------------------------------------------------
# a) MENU SETUP  (Harshil)
# ------------------------------------------------------------------
# The menu is a dictionary of dictionaries.
# Outer key   = category name
# Inner dict  = { item name : price }
MENU = {
    "Meals": {
        "Chicken Burger": 12000,
        "Beef Pilau": 10000,
        "Chapati and Beans": 6000,
    },
    "Drinks": {
        "Soda": 2500,
        "Fresh Juice": 4000,
        "Bottled Water": 1500,
    },
    "Snacks": {
        "Samosa": 1500,
        "Chips": 5000,
    },
}

# Predefined list of riders. Each rider is a dictionary so we can
# easily track whether they are free to take a new order.
RIDERS = [
    {"name": "Peter", "available": True},
    {"name": "Grace", "available": True},
    {"name": "John", "available": True},
]

# The stages an order must move through, in order.
STATUS_STAGES = ["Pending", "Out for Delivery", "Delivered"]

# Name of the file used to save orders between runs.
ORDER_FILE = "orders_log.txt"

# This list holds every order (loaded from file + new ones made now).
# Each order is a dictionary - see take_order() for its shape.
orders = []

# Keeps track of the next order number to hand out.
next_order_id = 1


def print_menu():
    """Print the restaurant menu, grouped by category."""
    print("\n===== CANTEEN MENU =====")
    for category, items in MENU.items():
        print(f"\n-- {category} --")
        for item_name, price in items.items():
            print(f"  {item_name:<20} UGX {price}")
    print("=========================")


# ------------------------------------------------------------------
# b) ORDER TAKING  (Harshil)
# ------------------------------------------------------------------
def calculate_delivery_fee(subtotal, distance_band):
    """
    Work out the delivery fee.
    The fee depends on how far the customer is (distance_band),
    but if the order is big enough we give free delivery.
    """
    if subtotal >= 50000:
        return 0  # big orders get free delivery

    if distance_band == "1":       # Near campus
        return 1000
    elif distance_band == "2":     # Medium distance
        return 3000
    elif distance_band == "3":     # Far from campus
        return 5000
    else:
        return 3000  # fallback fee if something odd was entered


def choose_distance_band():
    """Ask the attendant which distance band the customer is in."""
    print("\nDelivery distance:")
    print("  1. Near campus")
    print("  2. Medium distance")
    print("  3. Far from campus")
    band = input("Choose distance band (1-3): ").strip()
    while band not in ("1", "2", "3"):
        band = input("Please enter 1, 2 or 3: ").strip()
    return band


def take_order():
    """
    Let the attendant build an order for a customer.
    Returns the finished order as a dictionary, or None if cancelled.
    """
    global next_order_id

    print_menu()
    customer_name = input("\nEnter customer name: ").strip()
    if customer_name == "":
        customer_name = "Walk-in Customer"

    basket = {}   # item name -> quantity chosen

    while True:
        item_name = input(
            "\nType an item name to add (or 'done' to finish): "
        ).strip()

        if item_name.lower() == "done":
            break

        # look for the item in any category
        found_price = None
        for category in MENU:
            if item_name in MENU[category]:
                found_price = MENU[category][item_name]
                break

        if found_price is None:
            print("Sorry, that item is not on the menu. Check spelling.")
            continue

        # ask for quantity, validate it is a whole number > 0
        qty_text = input(f"How many '{item_name}'? ").strip()
        if not qty_text.isdigit() or int(qty_text) <= 0:
            print("Please enter a valid whole number greater than 0.")
            continue
        quantity = int(qty_text)

        # add to basket (add to existing quantity if item chosen again)
        if item_name in basket:
            basket[item_name] += quantity
        else:
            basket[item_name] = quantity

        print(f"Added {quantity} x {item_name} to the order.")

    if len(basket) == 0:
        print("No items were added. Order cancelled.")
        return None

    # calculate the subtotal by looking up each item's price again
    subtotal = 0
    for item_name, quantity in basket.items():
        for category in MENU:
            if item_name in MENU[category]:
                subtotal += MENU[category][item_name] * quantity

    distance_band = choose_distance_band()
    delivery_fee = calculate_delivery_fee(subtotal, distance_band)
    total = subtotal + delivery_fee

    order = {
        "id": next_order_id,
        "customer": customer_name,
        "items": basket,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
        "status": "Pending",
        "rider": None,
    }
    next_order_id += 1

    print(f"\nOrder #{order['id']} created.")
    print(f"Subtotal: UGX {subtotal}")
    print(f"Delivery fee: UGX {delivery_fee}")
    print(f"Total: UGX {total}")

    return order


# ------------------------------------------------------------------
# c) RIDER ASSIGNMENT AND STATUS TRACKING  (Oscar)
# ------------------------------------------------------------------
def assign_rider(order):
    """
    Give the order to the first available rider.
    If no rider is free, the order stays without a rider for now.
    """
    for rider in RIDERS:
        if rider["available"]:
            rider["available"] = False
            order["rider"] = rider["name"]
            print(f"Rider {rider['name']} has been assigned to order #{order['id']}.")
            return

    print("No riders are available right now. Order will wait for a rider.")


def free_up_rider(rider_name):
    """Mark a rider as available again once their delivery is done."""
    for rider in RIDERS:
        if rider["name"] == rider_name:
            rider["available"] = True
            return


def advance_status(order):
    """
    Move an order to its next status stage.
    Stages must happen in order, so we cannot skip ahead.
    """
    current_index = STATUS_STAGES.index(order["status"])

    if current_index == len(STATUS_STAGES) - 1:
        print(f"Order #{order['id']} is already Delivered. Nothing to do.")
        return

    next_status = STATUS_STAGES[current_index + 1]
    order["status"] = next_status
    print(f"Order #{order['id']} status changed to '{next_status}'.")

    # once delivered, the rider becomes free for the next order
    if next_status == "Delivered" and order["rider"] is not None:
        free_up_rider(order["rider"])


def show_riders():
    """Print each rider and whether they are currently free."""
    print("\n===== RIDER STATUS =====")
    for rider in RIDERS:
        state = "Available" if rider["available"] else "On a delivery"
        print(f"  {rider['name']:<10} - {state}")


# ------------------------------------------------------------------
# d) SALES AND REPORTING  (Churchill)
# ------------------------------------------------------------------
def show_sales_report():
    """Print total revenue, the best-selling item and status counts."""
    if len(orders) == 0:
        print("\nNo orders have been placed yet.")
        return

    total_revenue = 0
    item_totals = {}          # item name -> total quantity sold
    status_counts = {}        # status -> how many orders have it

    for order in orders:
        total_revenue += order["total"]

        for item_name, quantity in order["items"].items():
            if item_name in item_totals:
                item_totals[item_name] += quantity
            else:
                item_totals[item_name] = quantity

        status = order["status"]
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1

    # find the item with the highest quantity sold
    best_item = None
    best_quantity = 0
    for item_name, quantity in item_totals.items():
        if quantity > best_quantity:
            best_quantity = quantity
            best_item = item_name

    print("\n===== SALES REPORT =====")
    print(f"Total orders placed : {len(orders)}")
    print(f"Total revenue        : UGX {total_revenue}")
    if best_item is not None:
        print(f"Best-selling item    : {best_item} ({best_quantity} sold)")

    print("\nOrders by status:")
    for stage in STATUS_STAGES:
        count = status_counts.get(stage, 0)
        print(f"  {stage:<18}: {count}")


# ------------------------------------------------------------------
# e) FILE PERSISTENCE  (Alvin)
# ------------------------------------------------------------------
def items_to_text(items_dict):
    """Turn {'Soda': 2, 'Chips': 1} into the text 'Soda:2,Chips:1'."""
    pieces = []
    for item_name, quantity in items_dict.items():
        pieces.append(f"{item_name}:{quantity}")
    return ",".join(pieces)


def text_to_items(items_text):
    """Turn the text 'Soda:2,Chips:1' back into a dictionary."""
    items_dict = {}
    if items_text.strip() == "":
        return items_dict

    pieces = items_text.split(",")
    for piece in pieces:
        name_and_qty = piece.split(":")
        item_name = name_and_qty[0]
        quantity = int(name_and_qty[1])
        items_dict[item_name] = quantity
    return items_dict


def order_to_line(order):
    """Turn one order dictionary into a single line of text."""
    return "|".join([
        str(order["id"]),
        order["customer"],
        items_to_text(order["items"]),
        str(order["subtotal"]),
        str(order["delivery_fee"]),
        str(order["total"]),
        order["status"],
        str(order["rider"]),
    ])


def save_all_orders():
    """
    Rewrite the whole log file from the current 'orders' list.
    Called after any change (new order or status update) so the
    file on disk always matches what is on screen.
    """
    try:
        with open(ORDER_FILE, "w") as f:
            for order in orders:
                f.write(order_to_line(order) + "\n")
    except OSError:
        print("Warning: could not save orders to file.")


def load_orders_from_file():
    """
    Read past orders from the log file when the program starts.
    If the file is missing or a line is damaged, skip it quietly
    instead of crashing the program.
    """
    global next_order_id

    if not os.path.exists(ORDER_FILE):
        print("No previous order file found. Starting fresh.")
        return

    try:
        with open(ORDER_FILE, "r") as f:
            lines = f.readlines()
    except OSError:
        print("Warning: could not read the order file. Starting fresh.")
        return

    loaded_count = 0
    for line in lines:
        line = line.strip()
        if line == "":
            continue

        parts = line.split("|")
        if len(parts) != 8:
            print("Skipping a damaged line in the order file.")
            continue

        try:
            order = {
                "id": int(parts[0]),
                "customer": parts[1],
                "items": text_to_items(parts[2]),
                "subtotal": float(parts[3]),
                "delivery_fee": float(parts[4]),
                "total": float(parts[5]),
                "status": parts[6],
                "rider": None if parts[7] == "None" else parts[7],
            }
        except ValueError:
            print("Skipping a damaged line in the order file.")
            continue

        orders.append(order)
        loaded_count += 1

        # make sure new orders get an id number bigger than any loaded one
        if order["id"] >= next_order_id:
            next_order_id = order["id"] + 1

    print(f"Loaded {loaded_count} previous order(s) from file.")


# ------------------------------------------------------------------
# f) MENU-DRIVEN DRIVER PROGRAMME  (Alvin)
# ------------------------------------------------------------------
def view_all_orders():
    """Print a short summary line for every order placed so far."""
    if len(orders) == 0:
        print("\nThere are no orders yet.")
        return

    print("\n===== ALL ORDERS =====")
    for order in orders:
        print(
            f"#{order['id']} | {order['customer']:<15} | "
            f"UGX {order['total']:<8} | {order['status']:<16} | "
            f"Rider: {order['rider']}"
        )


def choose_order_by_id():
    """Ask for an order id and return the matching order, or None."""
    id_text = input("Enter order number: ").strip()
    if not id_text.isdigit():
        print("Please enter a valid number.")
        return None

    order_id = int(id_text)
    for order in orders:
        if order["id"] == order_id:
            return order

    print("No order found with that number.")
    return None


def main_menu():
    """The main loop that ties every part of the system together."""
    load_orders_from_file()

    while True:
        print("\n===================================")
        print("   CAMPUS FOOD DELIVERY SYSTEM")
        print("===================================")
        print("1. View Menu")
        print("2. Place New Order")
        print("3. View All Orders")
        print("4. Advance an Order's Status")
        print("5. View Rider Status")
        print("6. Sales Report")
        print("7. Exit")

        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            print_menu()

        elif choice == "2":
            new_order = take_order()
            if new_order is not None:
                assign_rider(new_order)
                orders.append(new_order)
                save_all_orders()

        elif choice == "3":
            view_all_orders()

        elif choice == "4":
            order = choose_order_by_id()
            if order is not None:
                advance_status(order)
                save_all_orders()

        elif choice == "5":
            show_riders()

        elif choice == "6":
            show_sales_report()

        elif choice == "7":
            print("Goodbye! Thank you for using the system.")
            break

        else:
            print("Please choose a number from 1 to 7.")


if __name__ == "__main__":
    main_menu()
