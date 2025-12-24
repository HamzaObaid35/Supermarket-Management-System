# Supermarket Management System

A complete supermarket management system built using **Python** and **Streamlit**.  
The application provides inventory management, sales processing, user authentication, and detailed sales reports.

---

## 📖 Overview

This project is a mini supermarket management system that helps manage products, track inventory, process sales, and generate reports.  
It supports **role-based access control**, allowing administrators and workers to perform different actions.

---

## 🎯 Features

- 🔐 User authentication with roles (Admin / Worker)
- 📦 Inventory management (Add, Update, Delete items)
- 🛒 Sell multiple items with automatic stock update
- 🧾 Sales logging and receipt generation
- 📊 Daily, monthly, and yearly sales reports
- ⚠️ Low stock and near-expiry alerts
- 📅 Sales history dashboard
- 📥 Export reports as CSV files

---

## 🧠 System Roles

### 👑 Admin (angel)
- Full access to all features
- Inventory control
- Sales reports and analytics

### 👷 Worker
- Add items
- Sell items

---

## ✅ Advantages

- Easy to use web interface
- Role-based access control
- Automated sales and inventory tracking
- Real-time reporting
- CSV-based lightweight storage


---

## ⚠ Limitations

- Uses local CSV files (not a database)
- Not designed for large-scale supermarkets
- No online multi-user synchronization

---
#  🚀 Future Improvements

- Replace CSV with a database (SQLite / PostgreSQL)
- Add barcode scanning
- Improve UI design
- Deploy online using Streamlit Cloud
- Add user management panel


---

## 🗂 Project Structure

```text
Supermarket-Management-System/
│
├── app.py
├── utils.py
├── test.py
├── users.json
│
├── data/
│   ├── inventory.csv
│   └── sales_log.csv
│
├── requirements.txt
└── README.md
```
---
## 👤 Author

- Hamza Mohammed
- FaresAlnamla
- Ahmed Alyazouri

