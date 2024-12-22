import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    """建立並返回數據庫連接"""
    try:
        connection = mysql.connector.connect(
            user="root",
            password="",
            host="localhost",
            port=3306,
            database="restaurant_platform"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"數據庫連接失敗: {e}")
        raise

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """輔助函數，用於執行數據庫查詢"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        conn.commit()
    except Error as e:
        print(f"執行查詢時發生錯誤: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 餐廳用戶管理
def register_restaurant(user_id, password):
    """註冊新餐廳用戶"""
    try:
        hashed_password = generate_password_hash(password)
        query = "INSERT INTO restaurants (user_id, password) VALUES (%s, %s)"
        execute_query(query, (user_id, hashed_password))
        return True
    except mysql.connector.IntegrityError as e:
        print(f"註冊失敗: {e}")
        return False

def login_restaurant(user_id, password):
    """驗證餐廳用戶登錄"""
    query = "SELECT * FROM restaurants WHERE user_id = %s"
    restaurant = execute_query(query, (user_id,), fetchone=True)
    if restaurant and check_password_hash(restaurant['password'], password):
        return True
    return False

# 菜單管理
def add_menu_item(name, description, price, restaurant_id, image_path):
    """添加新的菜單項"""
    query = """
        INSERT INTO menu_items (name, description, price, restaurant_id, image_path) 
        VALUES (%s, %s, %s, %s, %s)
    """
    execute_query(query, (name, description, price, restaurant_id, image_path))
    return True

def get_menu_items(restaurant_id=None):
    """獲取餐廳菜單項"""
    query = "SELECT * FROM menu_items"
    params = ()
    if restaurant_id:
        query += " WHERE restaurant_id = %s"
        params = (restaurant_id,)
    return execute_query(query, params, fetchall=True)

def edit_menu_item(item_id, name, description, price, restaurant_id, image_path=None):
    """編輯指定的菜單項，支持更新圖片路徑"""
    query = """
        UPDATE menu_items 
        SET name = %s, description = %s, price = %s
    """
    params = [name, description, price]

    # 如果提供了圖片路徑，則包含 image_path 的更新
    if image_path:
        query += ", image_path = %s"
        params.append(image_path)

    query += " WHERE id = %s AND restaurant_id = %s"
    params.extend([item_id, restaurant_id])

    execute_query(query, tuple(params))
    return True

def delete_menu_item(item_id, restaurant_id):
    """刪除指定的菜單項"""
    query = "DELETE FROM menu_items WHERE id = %s AND restaurant_id = %s"
    execute_query(query, (item_id, restaurant_id))
    return True

# 訂單管理
def get_orders(restaurant_id=None):
    """獲取訂單列表"""
    query = "SELECT * FROM orders ORDER BY created_at DESC"
    params = ()
    if restaurant_id:
        query = "SELECT * FROM orders WHERE restaurant_id = %s ORDER BY created_at DESC"
        params = (restaurant_id,)
    return execute_query(query, params, fetchall=True)

def get_order_details(order_id):
    """獲取訂單詳情"""
    order_query = "SELECT * FROM orders WHERE id = %s"
    order = execute_query(order_query, (order_id,), fetchone=True)

    items_query = """
        SELECT mi.name, mi.price, oi.quantity 
        FROM order_items oi
        JOIN menu_items mi ON oi.menu_item_id = mi.id
        WHERE oi.order_id = %s
    """
    order_items = execute_query(items_query, (order_id,), fetchall=True)

    return order, order_items

def update_order_status(order_id, status, restaurant_id):
    """更新訂單狀態"""
    query = """
        UPDATE orders 
        SET status = %s 
        WHERE id = %s AND restaurant_id = %s
    """
    execute_query(query, (status, order_id, restaurant_id))
    return True

def notify_rider_to_pickup(order_id, restaurant_id):
    """通知騎手取餐"""
    if update_order_status(order_id, "Ready for Pickup", restaurant_id):
        print(f"訂單 {order_id} 已準備好，已通知騎手取餐！")
        return True
    return False
    
def create_order(restaurant_id, customer_name, order_items):
    try:
        # 假设订单表名为 `orders`，订单项表名为 `order_items`
        order_id = insert_into_db(
            "INSERT INTO orders (restaurant_id, customer_name, status) VALUES (%s, %s, %s)",
            (restaurant_id, customer_name, 'Pending')
        )
        for item_id in order_items:
            insert_into_db(
                "INSERT INTO order_items (order_id, menu_item_id) VALUES (%s, %s)",
                (order_id, item_id)
            )
        return True
    except Exception as e:
        print(f"创建订单失败: {e}")
        return False
