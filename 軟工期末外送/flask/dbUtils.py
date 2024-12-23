#!/usr/local/bin/python
# Connect to MariaDB Platform
import mysql.connector #mariadb

try:
	#連線DB
	conn = mysql.connector.connect(
		user="root",
		password="",
		host="localhost",
		port=3306,
		database="delivery"
	)
	#建立執行SQL指令用之cursor, 設定傳回dictionary型態的查詢結果 [{'欄位名':值, ...}, ...]
	cursor=conn.cursor(dictionary=True)
except mysql.connector.Error as e: # mariadb.Error as e:
	print(e)
	print("Error connecting to DB")
	exit(1)


def add(jName,jCont,dDay):
	sql="insert into todolist (jobName,jobContent,dueDate,status) VALUES (%s,%s,%s,%s)"
	param=(jName,jCont,dDay,0,)
	cursor.execute(sql,param)
	conn.commit()
	return
	
def delete(id):
	sql="delete from 表格 where 條件"
	cursor.execute(sql,(id,))
	conn.commit()
	return

def update(id):
	sql="update todolist set status=1 where id=%s"
	param=(id,)
	cursor.execute(sql,param)
	conn.commit()
	return

def setFinish(id):
	sql="update todolist set status=1 where id=%s"
	param=(id,)
	cursor.execute(sql,param)
	conn.commit()
	return
	
def getList():
	sql="select id,jobName,jobContent,status,dueDate from todolist;"
	#param=('值',...)
	cursor.execute(sql)
	return cursor.fetchall()

def cursor1(user_id,user_password): 
    sql = "SELECT id, password FROM users WHERE id = %s AND password = %s"
    param = (user_id,user_password)
    cursor.execute(sql,param)
    user = cursor.fetchone()  # 獲取查詢結果
    return user  # 返回使用者資料

def addregister(user_id, username, password, created_at):
    # 將用戶資料插入到 users 表中
    sql_insert = "INSERT INTO users (id, username, password, created_at) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql_insert, (user_id, username, password, created_at))
    conn.commit()  # 提交更改
    return True  # 返回 True 表示註冊成功

def myitems(user_id):  
    sql = "SELECT id, name, description, base_price, current_highest_price, user_id, created_at FROM auctionitems WHERE user_id = %s"
    param = (user_id,)
    cursor.execute(sql, param)
    items = cursor.fetchall()  # 獲取所有符合條件的商品
    return items  # 返回商品列表er 

def additem(item_name,description,base_price,user_id,created_at):
	sql="insert into auctionitems (name,description,base_price,user_id,created_at) VALUES (%s,%s,%s,%s,%s)"
	param=(item_name,description,base_price,user_id,created_at)
	cursor.execute(sql,param)
	conn.commit()
	return

def delmyitems(item_id, user_id):
    # 從資料庫中刪除指定的項目
    sql_delete = "DELETE FROM auctionitems WHERE id = %s"
    cursor.execute(sql_delete, (item_id,))
    conn.commit()  # 確保更改已提交到資料庫
    
    # 現在檢索指定用戶的所有項目
    sql_select = "SELECT id, name, description, base_price, current_highest_price, user_id, created_at FROM auctionitems WHERE user_id = %s"
    cursor.execute(sql_select, (user_id,))
    return cursor.fetchall()  # 獲取所有記錄

def edititem(item_id, item_name=None, description=None, base_price=None, user_id=None, created_at=None):
    if item_name and description and base_price and user_id and created_at:
        # 更新操作
        sql = """
        UPDATE auctionitems 
        SET name = %s, description = %s, base_price = %s, user_id = %s, created_at = %s 
        WHERE id = %s
        """
        param = (item_name, description, base_price, user_id, created_at, item_id)
        cursor.execute(sql, param)
        conn.commit()
    else:
        # 查詢操作
        sql = "SELECT id, name, description, base_price, user_id, created_at FROM auctionitems WHERE id = %s"
        cursor.execute(sql, (item_id,))
        return cursor.fetchone()
    
def auction():
    # SQL 查询，将 auctionitems 中的 current_highest_price 与 bids 表的最高出价关联
    sql = """
    SELECT auctionitems.id,
           auctionitems.name,
           auctionitems.description,
           auctionitems.base_price,
           COALESCE(bids.max_bid_amount, auctionitems.base_price) AS current_highest_price,
           bids.max_bid_time AS highest_bid_time,  -- 最高出价的时间
           auctionitems.user_id,
           auctionitems.created_at
    FROM auctionitems
    LEFT JOIN (
        SELECT item_id, 
               MAX(bid_amount) AS max_bid_amount,  -- 获取每个 item_id 的最高出价金额
               MAX(created_at) AS max_bid_time  -- 获取对应的出价时间
        FROM bids
        GROUP BY item_id
    ) AS bids ON auctionitems.id = bids.item_id
    GROUP BY auctionitems.id;
    """
	# GROUP BY item_id：確保對每個項目只返回一條記錄
    cursor.execute(sql)  # 执行 SQL 查询
    return cursor.fetchall()  # 获取查询结果并返回

def bid(item_id=None):
    sql = """
    SELECT bids.id AS bid_id, 
           bids.item_id, 
           bids.bid_amount, 
           bids.bidder_id, 
           bids.created_at, 
           auctionitems.name AS item_name,  
           auctionitems.base_price, 
           auctionitems.current_highest_price 
    FROM bids
    JOIN auctionitems ON bids.item_id = auctionitems.id
    """
    
    # 如果提供了 item_id 参数，则添加 WHERE 子句
    if item_id:
        sql += " WHERE bids.item_id = %s"
        cursor.execute(sql, (item_id,))
    else:
        cursor.execute(sql)
    
    return cursor.fetchall()  # 获取查询结果并返回

def addprice(item_id, price, user_id, created_at): 
    # 查詢該商品在 bids 中的最高出價
    max_bid_query = """
    SELECT 
    COALESCE((SELECT MAX(bid_amount) FROM bids WHERE item_id = %s), 
                  (SELECT base_price FROM auctionitems WHERE id = %s)) AS price
    """
    cursor.execute(max_bid_query, (item_id, item_id))
    max_bid_result = cursor.fetchone()

    # 打印 max_bid_result 以檢查其結構
    print("Max Bid Result:", max_bid_result)

    # 提取最高出價或基準價格
    max_bid_price = 0
    if max_bid_result:
        # 如果是字典游標，使用鍵獲取價格
        max_bid_price = max_bid_result['price'] if isinstance(max_bid_result, dict) else max_bid_result[0]

    # 比較出價和最高出價或基準價格
    if float(price) <= float(max_bid_price):
        print("出價低於或等於最高出價或基準價格，出價無效")
        return "出價無效"  # 返回出價無效信息
    else:
        # 若出價有效，執行插入語句
        sql = "INSERT INTO bids (item_id, bid_amount, bidder_id, created_at) VALUES (%s, %s, %s, %s)"
        param = (item_id, price, user_id, created_at)
        cursor.execute(sql, param)
        conn.commit()
        print("出價成功，已插入資料")  # 打印成功信息
        return "出價成功"  # 返回成功訊息


 