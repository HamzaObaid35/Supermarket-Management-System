import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import os

# ---------- Setup ----------
DATA_PATH = "data"
INVENTORY_FILE = os.path.join(DATA_PATH, "inventory.csv")
SALES_LOG_FILE = os.path.join(DATA_PATH, "sales_log.csv")
USER_FILE = "users.json"

# ---------- Load Data ----------
def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        return pd.read_csv(INVENTORY_FILE)
    else:
        return pd.DataFrame(columns=["id", "name", "category", "price", "quantity", "expiry"])

def save_inventory(df):
    df.to_csv(INVENTORY_FILE, index=False)

def log_sale(sales):
    log_df = pd.DataFrame(sales)
    log_df = log_df[["datetime", "item_id", "item_name", "quantity", "unit_price", "total_price"]]  # Ensure correct columns
    if os.path.exists(SALES_LOG_FILE):
        existing = pd.read_csv(SALES_LOG_FILE)
        log_df = pd.concat([existing, log_df], ignore_index=True)
    log_df.to_csv(SALES_LOG_FILE, index=False)

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE) as f:
            return json.load(f)
    return {}

# ---------- Authentication ----------
def login():
    st.title("🔐 Supermarket Login")
    users = load_users()
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_data = users.get(username)
        if user_data and user_data["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user_data["role"]
            st.success(f"✅ Welcome {username} ({user_data['role']})")
        else:
            st.error("❌ Incorrect username or password")

# ---------- Functional Pages ----------
def add_item(df):
    st.subheader("➕ Add New Item")
    with st.form("add_form"):
        item_id = st.text_input("Item ID (4 digits)")
        name = st.text_input("Item Name")
        category = st.selectbox("Category", ["Produce", "Dairy", "Household", "Other"])
        price = st.number_input("Price (₪)", min_value=0.0, step=0.01)
        quantity = st.number_input("Quantity", min_value=0, step=1)
        expiry = st.date_input("Expiry Date")
        submitted = st.form_submit_button("Add Item")

        if submitted:
            if not item_id or not item_id.isdigit() or len(item_id) != 4:
                st.error("❌ Item ID must be exactly 4 digits.")
                return df
            if item_id in df["id"].astype(str).values:
                existing_name = df[df["id"].astype(str) == item_id]["name"].values[0]
                st.error(f"❌ Serial number already used for item: **{existing_name}**. Please use a different ID.")
                return df
            new_item = pd.DataFrame([{
                "id": item_id,
                "name": name,
                "category": category,
                "price": price,
                "quantity": quantity,
                "expiry": expiry
            }])
            df = pd.concat([df, new_item], ignore_index=True)
            save_inventory(df)
            st.success("✅ Item added successfully!")
    return df

def update_stock(df):
    st.subheader("🔄 Update Stock")
    if df.empty:
        st.info("Inventory is empty.")
        return df

    df["display"] = df["id"].astype(str) + " - " + df["name"]
    selection = st.selectbox("Select Item", df["display"].values)
    item_id = df[df["display"] == selection]["id"].values[0]

    new_qty = st.number_input("New Quantity", min_value=0, step=1)
    new_price = st.text_input("New Price (optional, leave blank to keep current)")

    if st.button("Update Stock"):
        df.loc[df["id"] == item_id, "quantity"] = new_qty
        if new_price:
            try:
                price_val = float(new_price)
                df.loc[df["id"] == item_id, "price"] = price_val
            except ValueError:
                st.warning("⚠️ Invalid price entered. Price not updated.")
        save_inventory(df)
        st.success(f"✅ Stock for item {selection} updated.")
    return df

def sell_item(df):
    st.subheader("🛒 Sell Multiple Items")
    if df.empty:
        st.info("Inventory is empty.")
        return df

    df["display"] = df["id"].astype(str) + " - " + df["name"]
    selected_items = st.multiselect("Select Items to Sell", df["display"].values)

    sales = []
    total_bill = 0

    for idx, display in enumerate(selected_items):
        item = df[df["display"] == display].iloc[0]
        qty = st.number_input(f"Quantity for {item['name']} (Available: {item['quantity']})", min_value=0, max_value=int(item['quantity']), step=1, key=f"qty_{item['id']}_{idx}")
        if qty > 0:
            df.loc[df["id"] == item["id"], "quantity"] -= qty
            total_price = float(item["price"]) * qty
            sales.append({
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "item_id": item["id"],
                "item_name": item["name"],
                "quantity": qty,
                "unit_price": float(item["price"]),
                "total_price": total_price
            })
            total_bill += total_price

    if st.button("Confirm Sale") and sales:
        save_inventory(df)
        log_sale(sales)
        st.success(f"✅ Sale complete. Total: ₪{total_bill:.2f}")
        if st.checkbox("💳 Print Receipt"):
            receipt = pd.DataFrame(sales)
            st.write("### 🧾 Receipt")
            st.dataframe(receipt)
    return df

def delete_item(df):
    st.subheader("🗑️ Delete Item")
    if df.empty:
        st.info("Inventory is empty.")
        return df

    df["display"] = df["id"].astype(str) + " - " + df["name"]
    selection = st.selectbox("Select Item to Delete", df["display"].values)
    item_id = df[df["display"] == selection]["id"].values[0]

    if st.button("Delete Item"):
        df = df[df["id"] != item_id]
        save_inventory(df)
        st.success(f"🗑️ Item {selection} deleted successfully.")
    return df

def view_inventory(df):
    st.subheader("📦 Inventory List")
    st.dataframe(df)

    st.markdown("### ⚠️ Low Stock or Expiring Soon")
    soon_expiring = df.copy()
    soon_expiring["expiry"] = pd.to_datetime(soon_expiring["expiry"], errors="coerce")
    soon_expiring = soon_expiring[(soon_expiring["quantity"] <= 5) | (soon_expiring["expiry"] <= datetime.now() + timedelta(days=7))]
    if not soon_expiring.empty:
        st.warning("The following items are low in stock or expiring within 7 days:")
        st.dataframe(soon_expiring)
    else:
        st.success("No items are low in stock or near expiry.")

def daily_sales_report():
    st.subheader("📊 Daily Sales Report")
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(SALES_LOG_FILE):
        df = pd.read_csv(SALES_LOG_FILE)
        today_sales = df[df["datetime"].str.startswith(today)]
        total_sales = today_sales["total_price"].sum()
        st.write(f"🗓️ **Date:** {today}")
        st.write(f"🛍️ **Total Sales Today:** ₪{total_sales:.2f}")
        st.dataframe(today_sales)
    else:
        st.info("No sales recorded yet.")

def sales_report_summary():
    st.subheader("📈 Sales Report (Day / Month / Year)")
    if not os.path.exists(SALES_LOG_FILE):
        st.info("No sales data available.")
        return
    df = pd.read_csv(SALES_LOG_FILE)
    df["datetime"] = pd.to_datetime(df["datetime"])
    today = datetime.now().date()
    df_today = df[df["datetime"].dt.date == today]
    df_month = df[df["datetime"].dt.month == today.month]
    df_year = df[df["datetime"].dt.year == today.year]
    total_today = df_today["total_price"].sum()
    total_month = df_month["total_price"].sum()
    total_year = df_year["total_price"].sum()
    st.write(f"🗓️ **Total Sales Today:** ₪{total_today:.2f}")
    st.write(f"📆 **Total Sales This Month:** ₪{total_month:.2f}")
    st.write(f"📅 **Total Sales This Year:** ₪{total_year:.2f}")
    st.markdown("### 📅 Download Summary Report")
    report_df = pd.DataFrame({
        "Period": ["Today", "This Month", "This Year"],
        "Total Sales (₪)": [total_today, total_month, total_year]
    })
    csv = report_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV Report",
        data=csv,
        file_name=f"sales_report_{today}.csv",
        mime='text/csv'
    )
def sales_history_dashboard():
    st.subheader("📅 Sales History Dashboard")
    if not os.path.exists(SALES_LOG_FILE):
        st.info("No sales data available.")
        return
    df = pd.read_csv(SALES_LOG_FILE)
    df["datetime"] = pd.to_datetime(df["datetime"])
    available_dates = df["datetime"].dt.date.unique()
    selected_date = st.date_input("Select Date", min_value=min(available_dates), max_value=max(available_dates))
    df_selected = df[df["datetime"].dt.date == selected_date]
    total_selected = df_selected["total_price"].sum()
    st.write(f"🛍️ **Total Sales on {selected_date}:** ₪{total_selected:.2f}")
    st.dataframe(df_selected)
    if st.checkbox("📥 Download This Day's Sales"):
        csv = df_selected.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download Sales {selected_date}",
            data=csv,
            file_name=f"sales_{selected_date}.csv",
            mime='text/csv'
        )


# ---------- Main App ----------
def main():
    st.set_page_config("Supermarket Management", layout="wide")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login()
        return

    role = st.session_state.get("role", "worker")

    if role == "angel":
        menu_options = [
        "Add Item", "Update Stock", "Sell Item", "Delete Item", "View Inventory", 
        "Daily Sales Report", "Full Sales Summary", "Sales History Dashboard", "Logout"
    ]

    else:
        menu_options = ["Add Item", "Sell Item", "Logout"]

    st.sidebar.title("📋 Menu")
    option = st.sidebar.radio("Navigate", menu_options)
    df = load_inventory()


    if option == "Add Item":
        df = add_item(df)
    elif option == "Update Stock":
        df = update_stock(df)
    elif option == "Sell Item":
        df = sell_item(df)
    elif option == "Delete Item":
        df = delete_item(df)
    elif option == "View Inventory":
        view_inventory(df)
    elif option == "Daily Sales Report":
        daily_sales_report()
    elif option == "Sales History Dashboard":
        sales_history_dashboard()

    elif option == "Full Sales Summary":
        sales_report_summary()
    elif option == "Logout":
        st.session_state.logged_in = False
        st.rerun()

if __name__ == "__main__":
    main()
