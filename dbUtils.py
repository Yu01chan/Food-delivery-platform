import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict  # 載入 defaultdict

def get_db_connection():
    """建立並返回資料庫連接"""
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
        print(f"資料庫連接失敗: {e}")
        raise

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """輔助函數，用於執行資料庫查詢"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = None

        # 根據需要提取單條或多條記錄
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        
        # 提交事務
        conn.commit()
        return result
    except Error as e:
        print(f"執行查詢時發生錯誤: {e}")
        raise
    finally:
        # 確保游標和連接關閉
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
    # 查询订单信息
    order_query = "SELECT * FROM orders WHERE id = %s"
    order = execute_query(order_query, (order_id,), fetchone=True)

    # 确保订单存在
    if order:
        # 解析订单项字段（假设它是以 '&' 分隔的字符串）
        order_items_str = order['order_items']  # 假设 'order_items' 是一个字符串
        order_items = []
        if order_items_str:
            items = order_items_str.split('&')  # 按照 '&' 分割字符串
            for item in items:
                try:
                    # 尝试解析每个订单项，例如：'炒飯 1'
                    name, quantity = item.split(' ')
                    order_items.append({'name': name, 'quantity': int(quantity)})
                except ValueError:
                    # 如果解析失败，记录警告信息
                    print(f"警告：无法解析订单项 '{item}'，格式不正确")
        return order, order_items

    return None, None  # 如果订单不存在，返回 None


def update_order_status(order_id, status, restaurant_id):
    """更新訂單狀態"""
    query = """
        UPDATE orders 
        SET status = %s 
        WHERE id = %s AND restaurant_id = %s
    """
    try:
        execute_query(query, (status, order_id, restaurant_id))
        return True
    except Exception as e:
        print(f"更新訂單狀態失敗: {e}")
        return False

def notify_rider_to_pickup(order_id, restaurant_id):
    """通知騎手取餐"""
    if update_order_status(order_id, "Ready for Pickup", restaurant_id):
        print(f"訂單 {order_id} 已準備好，已通知騎手取餐！")
        return True
    return False

#顧客
# 定義獲取菜單項目的函數
def get_menu_items_customer_data():
    """獲取所有餐廳的菜單項"""
    query = "SELECT * FROM menu_items"
    menu_items = execute_query(query, fetchall=True)  # 獲取所有菜單資料
    
    # 根據 restaurant_id 將菜單項目分組
    grouped_menu_items = defaultdict(list)
    for item in menu_items:
        grouped_menu_items[item['restaurant_id']].append(item)  # 確保 restaurant_id 為字串
    
    return grouped_menu_items

def get_menu_restaurant_data(restaurant_id):
    """ 獲取指定餐廳的菜單項 """
    query = "SELECT * FROM menu_items WHERE restaurant_id = %s"
    params = (restaurant_id,)
    return execute_query(query, params, fetchall=True)

# 根據商品ID獲取菜單項
def cartmenu_items(id):
    query = "SELECT id, name, price, restaurant_id FROM menu_items WHERE id = %s"
    params = (id,)
    return execute_query(query, params, fetchone=True)

def checkout_items(item_id):
    query = "SELECT restaurant_id, name, price FROM menu_items WHERE id = %s"
    params = (item_id,)
    return execute_query(query, params, fetchone=True)

def Send_order(restaurant_id, user_id, item_id_and_quantity, total_price):
    """插入訂單資料到 orders 表"""
    try:
        # 格式化 order_items，將 item_id 和 quantity 合併
        formatted_order_items = "; ".join([f"{item_id}&{quantity}" for item_id, quantity in item_id_and_quantity])

        # SQL 插入語句
        query = """
            INSERT INTO orders (
                restaurant_id, user_id, order_items, customer_total
            ) VALUES (%s, %s, %s, %s)
        """
        params = (
            restaurant_id, 
            user_id,
            formatted_order_items,  # 格式化後的 item_id&quantity
            total_price
        )

        # 使用 mysql.connector 來進行資料庫連接和執行
        connection = mysql.connector.connect(host='localhost', user='root', password='', db='restaurant_platform')
        cursor = connection.cursor()

        # 執行插入操作
        cursor.execute(query, params)
        connection.commit()

        # 獲取插入資料的ID（自動生成的 order_id）
        order_id = cursor.lastrowid

        # 關閉連接
        cursor.close()
        connection.close()

        if order_id:
            return order_id
        else:
            return None
    except Exception as e:
        print(f"插入訂單失敗: {e}")
        return None

def get_user_orders(user_id):
    """根據用戶 ID 獲取該用戶的所有訂單"""
    query = """
    SELECT 
        id, 
        restaurant_id, 
        order_items, 
        customer_total, 
        status, 
        reviewed, 
        created_at 
    FROM orders 
    WHERE user_id = %s
    """
    orders = execute_query(query, (user_id,), fetchall=True)
    return orders

def submit_order_review(order_id, rating, comment):
    """保存訂單評價並更新訂單狀態"""
    try:
        # 插入評價
        query = """
            INSERT INTO order_reviews (order_id, rating, comment, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        execute_query(query, (order_id, rating, comment))

        # 更新訂單狀態為已評價
        update_query = "UPDATE orders SET reviewed = 1 WHERE id = %s"
        execute_query(update_query, (order_id,))

    except Exception as e:
        print(f"保存訂單評價失敗: {e}")
        raise

#外送員
def get_rider_orders(rider_status=None):
    """根据外送员状态获取订单列表，支持不传递状态参数"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if rider_status:
                # 如果传递了 rider_status，则按状态过滤
                cursor.execute("""
                    SELECT * FROM orders
                    WHERE rider_delivery_status = %s
                """, (rider_status,))
            else:
                # 如果没有传递 rider_status，则返回所有 "Not Assigned" 或 "Pending" 状态的订单
                cursor.execute("""
                    SELECT * FROM orders
                    WHERE rider_delivery_status = 'Not Assigned' OR rider_delivery_status = 'Pending'
                """)

            orders = cursor.fetchall()
            conn.close()
            return orders
        except Exception as e:
            # 如果执行 SQL 查询时出现问题，捕获异常并打印
            print(f"Error executing query: {e}")
            conn.close()
            return []  # 发生错误时返回空列表
    else:
        print("Database connection failed.")
        return []  # 如果连接失败，返回空列表


def is_order_assigned(order_id):
    """检查订单是否已被外送员接取"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT rider_id FROM orders
            WHERE id = %s AND rider_delivery_status != 'Not Assigned'
        """, (order_id,))
        order = cursor.fetchone()
        conn.close()
        return order is not None  # 如果订单已经被分配，则返回 True
    return False


def assign_order_to_rider(order_id, rider_id):
    """将订单分配给外送员并更新状态"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET rider_delivery_status = 'Picked Up', rider_id = %s
            WHERE id = %s AND rider_delivery_status = 'Not Assigned'
        """, (rider_id, order_id))
        conn.commit()
        conn.close()
        return True  # 订单成功分配
    return False  # 订单分配失败
    
def get_order_by_id_and_rider(order_id, rider_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM orders WHERE id = %s AND rider_id = %s
    """, (order_id, rider_id))
    order = cursor.fetchone()
    conn.close()
    return order
    
def update_order_status_to_on_the_way(order_id, rider_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET rider_delivery_status = 'On the Way'
            WHERE id = %s AND rider_id = %s
        """, (order_id, rider_id))
        conn.commit()
        conn.close()
        
# 更新订单状态为 'Delivered'
def update_order_status_to_delivered(order_id, rider_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET rider_delivery_status = 'Delivered'
            WHERE id = %s AND rider_id = %s
        """, (order_id, rider_id))
        conn.commit()
        conn.close()


def fetch_orders_by_rider(rider_id):
    """根据外送员ID获取待取餐订单，状态为 'picked up' 或 'On the way'"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # 使用字典游标以便返回字典格式的结果
    cursor.execute("""
        SELECT * FROM orders 
        WHERE rider_id = %s AND rider_delivery_status IN ('picked up', 'On the way')
    """, (rider_id,))  # 使用元组来传递参数
    
    orders = cursor.fetchall()  # 获取所有符合条件的订单
    conn.close()
    return orders








