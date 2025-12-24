import csv, json

def load_inventory(filepath):
    try:
        with open(filepath, newline='') as csvfile:
            return list(csv.DictReader(csvfile))
    except FileNotFoundError:
        return []

def save_inventory(inventory, filepath):
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=inventory[0].keys())
        writer.writeheader()
        writer.writerows(inventory)

def display_inventory(inventory):
    print("\nID | Name | Category | Price | Qty | Expiry")
    print("-" * 50)
    for item in inventory:
        print(f"{item['id']} | {item['name']} | {item['category']} | ${item['price']} | {item['quantity']} | {item['expiry']}")

def authenticate(user_file):
    username = input("Username: ")
    password = input("Password: ")
    with open(user_file) as f:
        users = json.load(f)
    return users.get(username) == password
