import sqlite3
import json
import pdfplumber
import os

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price REAL,
            stock_available INTEGER,
            rating REAL,
            description TEXT,
            return_eligible BOOLEAN,
            delivery_time_days INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            products_json TEXT,
            order_status TEXT,
            order_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_text TEXT,
            source_page INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            product_name TEXT,
            question TEXT,
            answer TEXT
        )
    ''')

    conn.commit()
    return conn

def load_products(conn, filename="product_catalog.json"):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            items = data if isinstance(data, list) else data.get("products", [])
            
            print(f"Loading {len(items)} products...")
            cursor = conn.cursor()
            for p in items:
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (product_id, product_name, category, price, stock_available, rating, description, return_eligible, delivery_time_days)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    p.get("product_id"),
                    p.get("product_name"),
                    p.get("category"),
                    p.get("price"),
                    p.get("stock_available"),
                    p.get("rating"),
                    p.get("description"),
                    p.get("return_eligible"),
                    p.get("delivery_time_days")
                ))
            conn.commit()
    except Exception as e:
        print(f"Error loading products: {e}")

def load_orders(conn, filename="order_database.json"):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            items = data if isinstance(data, list) else data.get("orders", [])
            
            print(f"Loading {len(items)} orders...")
            cursor = conn.cursor()
            for o in items:
                products_str = json.dumps(o.get("products", []))
                cursor.execute('''
                    INSERT OR REPLACE INTO orders 
                    (order_id, customer_id, products_json, order_status, order_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    o.get("order_id"),
                    o.get("customer_id"),
                    products_str,
                    o.get("order_status"),
                    o.get("order_date")
                ))
            conn.commit()
    except Exception as e:
        print(f"Error loading orders: {e}")

def load_faqs(conn, filename="product_faqs.json"):
    if not os.path.exists(filename):
        print("FAQ file not found.")
        return
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            items = data if isinstance(data, list) else data.get("product_faqs", [])
            
            print(f"Loading FAQs for {len(items)} products...")
            cursor = conn.cursor()
            for item in items:
                p_id = item.get("product_id")
                p_name = item.get("product_name")
                
                for faq in item.get("faqs", []):
                    cursor.execute('''
                        INSERT INTO faqs (product_id, product_name, question, answer) 
                        VALUES (?, ?, ?, ?)
                    ''', (p_id, p_name, faq.get("question"), faq.get("answer")))
            conn.commit()
    except Exception as e:
        print(f"Error loading FAQs: {e}")

def load_policies(conn, filename="company_policies.pdf"):
    if not os.path.exists(filename):
        print("PDF file not found.")
        return

    try:
        print("Processing PDF policies...")
        cursor = conn.cursor()
        with pdfplumber.open(filename) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    cursor.execute('INSERT INTO policies (section_text, source_page) VALUES (?, ?)', (text, i+1))
        conn.commit()
    except Exception as e:
        print(f"Error loading PDF: {e}")

if __name__ == "__main__":
    conn = init_db()
    load_products(conn)
    load_orders(conn)
    load_policies(conn)
    load_faqs(conn)
    conn.close()
    print("\nSUCCESS: 'database.db' created successfully.")
