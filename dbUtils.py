import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict  # 載入 defaultdict

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
        result = None

        # 根据需要提取单条或多条记录
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        
        # 提交事务
        conn.commit()
        return result
    except Error as e:
        print(f"執行查詢時發生錯誤: {e}")
        raise
    finally:
        # 确保游标和连接关闭
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 餐廳用戶管理
def register_users(user_id, password, role): 
    """註冊新用戶"""
    try:
        hashed_password = generate_password_hash(password)
        query = "INSERT INTO users (user_id, password, role) VALUES (%s, %s, %s)"
        execute_query(query, (user_id, hashed_password, role))  # 增加 role 欄位
        return True
    except mysql.connector.IntegrityError as e:
        print(f"註冊失敗: {e}")
        return False

def login_users(user_id, password): 
    """驗證用戶登錄"""
    query = "SELECT * FROM users WHERE user_id = %s"
    user = execute_query(query, (user_id,), fetchone=True)
    if user and check_password_hash(user['password'], password):
        return user  # 返回整個 user 資料（包含 role）
    return None

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

# 定義獲取菜單項目的函數
def get_menu_items_customer_data():
    """獲取所有餐廳的菜單項"""
    query = "SELECT * FROM menu_items"
    menu_items = execute_query(query, fetchall=True)  # 獲取所有菜單資料
    
    # 根據 restaurant_id 將菜單項目分組
    grouped_menu_items = defaultdict(list)
    for item in menu_items:
        grouped_menu_items[item['restaurant_id']].append(item)# 確保 restaurant_id 為字串
    
    return grouped_menu_items

def get_menu_restaurant_data(restaurant_id):
    """ 获取指定餐厅的菜单项 """
    query = "SELECT * FROM menu_items WHERE restaurant_id = %s"
    params = (restaurant_id,)
    return execute_query(query, params, fetchall=True)

# 根据商品ID获取菜单项
def cartmenu_items(id):
    query = "SELECT id, name, price, restaurant_id FROM menu_items WHERE id = %s"
    params = (id,)
    return execute_query(query, params, fetchone=True)

def checkout_items(item_id):
    query = "SELECT restaurant_id, name, price FROM menu_items WHERE id = %s"
    params = (item_id,)
    return execute_query(query, params, fetchone=True)

def insert_into_db(query, params):
    """通用插入数据到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print(f"Executing query: {query} with params: {params}")  # 打印查询和参数
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0  # 返回是否插入成功
    except Exception as e:
        print(f"数据库操作失败: {e}")  # 打印错误信息
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def Send_order(restaurant_id, user_id, item_id_and_quantity, total_price):
    """插入订单数据到 orders 表"""
    
    # 格式化 order_items，将 item_id 和 quantity 合并
    formatted_order_items = f"{item_id_and_quantity[0]}&{item_id_and_quantity[1]}"  # 使用 & 分隔 item_id 和 quantity
    
    query = """
        INSERT INTO orders (
            restaurant_id, customer_id, order_items, customer_total
        ) VALUES (%s, %s, %s, %s)
    """
    params = (
        restaurant_id, 
        user_id,
        formatted_order_items,  # 格式化后的 item_id&quantity
        total_price
    )
    
    if insert_into_db(query, params):  # 如果插入成功
        # 获取插入数据的ID（自动生成的order_id）
        order_id = cursor.lastrowid  # 获取插入后的自增ID
        return order_id
    else:
        return None






