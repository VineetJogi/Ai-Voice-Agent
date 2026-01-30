import sqlite3
import json

DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def search_products(query: str, category: str = None, max_price: int = None):
    """
    Searches for products in the catalog.
    Args:
        query: The search keyword (e.g., 'battery', 'shoe').
        category: (Optional) The category to filter by.
        max_price: (Optional) The maximum price allowed.
    """
    print(f"   [Tool] Searching for: {query}")  # Debug print
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
    
    results = [f"{row['product_name']} (Price: {row['price']}, Stock: {row['stock_available']})" for row in rows]
    return "\n".join(results[:5])

def get_order_status(order_id: str):
    """
    Retrieves the status of a specific order.
    Args:
        order_id: The exact Order ID (e.g., 'O0001').
    """
    print(f"   [Tool] Checking Order: {order_id}") # Debug print
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return "Order ID not found in database."
    
    # Handle simple text status or complex JSON
    try:
        if '{' in str(row['products_json']):
            products_list = json.loads(row['products_json'])
            product_names = ", ".join([p['product_name'] for p in products_list])
        else:
            product_names = row['products_json'] # Handle if it's just plain text
            
        return f"Order {order_id}: {row['order_status']}. Placed on {row['order_date']}. Items: {product_names}."
    except:
        return f"Order {order_id}: {row['order_status']}."

def get_policy_info(topic: str):
    """
    Retrieves policy details for a topic.
    Args:
        topic: The policy topic (e.g., 'return', 'warranty').
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT section_text FROM policies WHERE section_text LIKE ?", (f"%{topic}%",))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No specific policy found for that topic."
    return rows[0]['section_text'][:600]

def get_product_faq(product_name: str, topic: str):
    """
    Looks up FAQs for a product.
    Args:
        product_name: The name of the product (e.g., 'Luma').
        topic: The question topic (e.g., 'battery', 'charge').
    """
    print(f"   [Tool] FAQ Search -> Product: {product_name}, Topic: {topic}") # Debug print
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT question, answer FROM faqs WHERE product_name LIKE ? AND question LIKE ?"
    cursor.execute(sql, (f"%{product_name}%", f"%{topic}%"))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return f"No FAQ found for {product_name} regarding {topic}."
    
    results = [f"Q: {row['question']}\nA: {row['answer']}" for row in rows]
    return "\n".join(results[:3])