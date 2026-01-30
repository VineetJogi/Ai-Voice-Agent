import sqlite3
import json

DB_NAME = "store.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def search_products(query, category=None, max_price=None):
    """
    Searches for products based on name, category, or price.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT product_name, price, stock_available, rating FROM products WHERE 1=1"
    params = []
    
    if query:
        sql += " AND product_name LIKE ?"
        params.append(f"%{query}%")
    if category:
        sql += " AND category LIKE ?"
        params.append(f"%{category}%")
    if max_price:
        sql += " AND price <= ?"
        params.append(max_price)
        
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No products found matching criteria."
    
    results = [f"{row['product_name']} (Price: {row['price']}, Stock: {row['stock_available']}, Rating: {row['rating']})" for row in rows]
    return "\n".join(results[:5])

def get_order_status(order_id):
    """
    Retrieves status and details for a specific order ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return "Order ID not found."
    
    products_list = json.loads(row['products_json'])
    product_names = ", ".join([p['product_name'] for p in products_list])
    
    return f"Order {order_id}: {row['order_status']}. Placed on {row['order_date']}. Items: {product_names}."

def get_policy_info(topic):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT section_text FROM policies WHERE section_text LIKE ?", (f"%{topic}%",))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No specific policy found for that topic."
    return rows[0]['section_text'][:600] + "..."

def get_product_faq(product_name_query, topic):
    """
    Looks up FAQs for a specific product and topic (e.g., 'Luma', 'battery').
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT product_name, question, answer FROM faqs WHERE product_name LIKE ? AND question LIKE ?"
    cursor.execute(sql, (f"%{product_name_query}%", f"%{topic}%"))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return f"I couldn't find an FAQ for '{product_name_query}' about '{topic}'."
    
    results = [f"Q: {row['question']}\nA: {row['answer']}" for row in rows]
    return "\n".join(results[:3])

if __name__ == "__main__":
    print("--- Testing Database Tools ---")
    print(get_order_status("O0001"))
    print("\n--- Testing FAQ Tool ---")
    print(get_product_faq("Luma", "battery"))
