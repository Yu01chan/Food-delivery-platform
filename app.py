from flask import Flask, render_template, request, session, redirect, url_for, flash
from functools import wraps
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, FloatField
from wtforms.validators import DataRequired, Length
from flask import session, redirect, url_for, request, render_template
from flask import jsonify
import dbUtils
import uuid
import os
from dbUtils import (
    register_users, login_users, add_menu_item, get_menu_items,
    edit_menu_item, delete_menu_item, get_orders, get_order_details,
    update_order_status, notify_rider_to_pickup,
    get_menu_items_customer_data,get_menu_restaurant_data,
    cartmenu_items,checkout_items,execute_query,Send_order,get_user_orders,submit_order_review,
    get_rider_orders, is_order_assigned, assign_order_to_rider,fetch_orders_by_rider,update_order_status_to_delivered,update_order_status_to_on_the_way,
    get_order_by_id_and_rider
)                                                                                              
app = Flask(__name__)                                                                          
app.config['SECRET_KEY'] = '123TyU%^&'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制最大上傳文件為 16MB



# Utility Functions
def allowed_file(filename):
    # 使用 MIME 類型確保文件的安全性
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        try:
            file.save(file_path)
            return file_path
        except Exception as e:
            flash(f"文件上傳失敗: {str(e)}")
            return None
    flash("不支持的文件格式或文件太大")
    return None

# Form Definitions
class MenuItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    description = StringField("Description", validators=[Length(max=500)])
    price = FloatField("Price", validators=[DataRequired()])
    image = FileField("Upload Image")
    submit = SubmitField("Submit")


# Authentication Decorator
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("請先登入")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route("/users", methods=["GET", "POST"]) 
def users():
    if request.method == "POST":
        user_id = request.form['user_id']
        password = request.form['password']
        role = request.form['role']  # 獲取角色
        
        # 根據角色選擇性處理地址或電話
        address = None
        phone = None
        if role == "restaurant" or role == "customer":
            address = request.form.get('address', None)
        elif role == "delivery":
            phone = request.form.get('phone', None)
        
        # 呼叫 register_users 函數，將 address 和 phone 傳入
        if register_users(user_id, password, role, address=address, phone=phone):
            flash("註冊成功！請登入")
            return redirect(url_for('login'))
        else:
            flash("註冊失敗，帳號可能已存在")
    
    return render_template("users.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form['user_id']
        password = request.form['password']
        user = login_users(user_id, password)  # 使用 login_users 函數來獲取用戶資料
        if user:
            session['user_id'] = user_id
            # 根據 role 值決定跳轉頁面
            if user['role'] == 'restaurant':
                return redirect(url_for('index'))  # 如果是餐廳用戶，跳轉到 /index
            elif user['role'] == 'customer':
                return redirect(url_for('customermenu'))  # 如果是顧客，跳轉到 /customermenu
            elif user['role'] == 'delivery':
                return redirect(url_for('rider_dashboard'))  # 如果是外送員，跳轉到 /rider_dashboard
        else:
            flash("登入失敗，請檢察您的帳密")
    return render_template("login.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/menu")
@login_required
def menu_list():
    restaurant_id = session.get('user_id')
    menu_items = get_menu_items(restaurant_id)

    # 確保圖片路徑為有效的靜態資源
    for item in menu_items:
        if item.get('image_path'):
            item['image_path'] = item['image_path'].replace("\\", "/")

    return render_template("menu_list.html", menu_items=menu_items)


@app.route("/add_menu_item", methods=["GET", "POST"])
def add_menu_item_route():
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']

        # 上傳圖片並確保路徑
        image_path = save_uploaded_file(image)
        if not image_path:
            flash("圖片上傳失敗，請重新嘗試！")
            return redirect(url_for("add_menu_item_route"))

        # 保存菜單項到數據庫
        restaurant_id = session.get('user_id')
        if add_menu_item(name, description, price, restaurant_id, image_path):
            flash("菜單添加成功！")
            return redirect(url_for("menu_list"))
        else:
            flash("添加菜單失敗，請稍後再試！")

    return render_template("add_menu_item.html")

@app.route("/edit_menu_item/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_menu_item_route(item_id):
    restaurant_id = session.get('user_id')
    menu_item = next(
        (item for item in get_menu_items(restaurant_id) if item['id'] == item_id), None
    )
    if not menu_item:
        flash("菜單項未找到。")
        return redirect(url_for("menu_list"))

    # 初始化表單並填充默認值
    form = MenuItemForm(
        name=menu_item.get("name"),
        description=menu_item.get("description"),
        price=menu_item.get("price")
    )

    # 當前圖片路徑修正，用於顯示和儲存
    current_image_path = menu_item.get('image_path', '').replace("\\", "/")
    display_image_path = (
        url_for('static', filename=current_image_path) if current_image_path else None
    )

    if form.validate_on_submit():
        # 處理圖片上傳
        if form.image.data:
            new_image_path = save_uploaded_file(form.image.data)
            if not new_image_path:
                flash("圖片上傳失敗，請重新嘗試。")
                return redirect(url_for("edit_menu_item_route", item_id=item_id))
            current_image_path = new_image_path.replace("\\", "/")

        # 更新菜單項
        if edit_menu_item(
            item_id,
            form.name.data,
            form.description.data,
            form.price.data,
            restaurant_id,
            current_image_path
        ):
            flash("菜單項更新成功！")
            return redirect(url_for("menu_list"))

        flash("更新菜單項失敗。")

    return render_template(
        "edit_menu_item.html",
        form=form,
        menu_item=menu_item,
        display_image_path=display_image_path
    )


@app.route("/delete_menu_item/<int:item_id>", methods=["POST"])
@login_required
def delete_menu_item_route(item_id):
    restaurant_id = session.get('user_id')
    if delete_menu_item(item_id, restaurant_id):
        flash("菜單項刪除成功！")
    else:
        flash("刪除菜單項失敗。")
    return redirect(url_for("menu_list"))

@app.route("/orders")
@login_required
def orders():
    restaurant_id = session.get('user_id')
    orders = get_orders(restaurant_id)
    return render_template("orders.html", orders=orders)

@app.route("/order/<int:order_id>")
@login_required
def order_details(order_id):
    order, order_items = get_order_details(order_id)
    if not order:  # 如果訂單不存在，返回錯誤
        flash("訂單不存在！")
        return redirect(url_for("orders"))
    return render_template("order_details.html", order=order, order_items=order_items)



@app.route("/update_order_status/<int:order_id>", methods=["POST"])
@login_required
def update_order_status_route(order_id):
    new_status = request.form['status']
    if not new_status:
        flash("無效得狀態！")
        return redirect(url_for("order_details", order_id=order_id))
    restaurant_id = session.get('user_id')
    if update_order_status(order_id, new_status, restaurant_id):
        flash("訂單狀態更新成功！")
    else:
        flash("更新訂單狀態失敗。")
    return redirect(url_for("orders"))



@app.route("/notify_rider/<int:order_id>", methods=["POST"])
@login_required
def notify_rider(order_id):
    restaurant_id = session.get('user_id')
    if notify_rider_to_pickup(order_id, restaurant_id):
        flash("外送員已被通知去取餐。")
    else:
        flash("通知外送員失敗。")
    return redirect(url_for("orders"))

@app.route("/logout")
@login_required
def logout():
    session.pop('user_id', None)
    flash("已註銷，歡迎再次登入！")
    return redirect(url_for('login'))

#顧客
@app.route('/customermenu')
@login_required
def customermenu():
    # 呼叫函數獲取菜單資料並進行分組
    grouped_menu_items = get_menu_items_customer_data()

    # 確保圖片路徑為有效的靜態資源
    for restaurant_id, menu_items in grouped_menu_items.items():
        for item in menu_items:
            if item.get('image_path'):
                item['image_path'] = item['image_path'].replace("\\", "/")

    # 傳遞正確的變數名稱
    return render_template("customermenu.html", menu_items=grouped_menu_items)

@app.route("/food/<restaurant_id>")
@login_required
def get_menu_restaurant(restaurant_id):
    # 獲取指定餐廳菜單項
    menu_items = get_menu_restaurant_data(restaurant_id)

    # 確保圖片路徑為有效的靜態資源
    for item in menu_items:
        if item.get('image_path'):
            # 確保圖片路徑相對於靜態文件夾
            item['image_path'] = item['image_path'].replace("\\", "/")

    return render_template("ordermenu.html", menu_items=menu_items)

# 選擇商品數量
@app.route('/cart_item/<int:item_id>', methods=['GET'])
@login_required
def view_cart_item(item_id):
    # 獲取商品消息
    item = cartmenu_items(item_id)
    if not item:
        flash('商品未找到')
        return "商品未找到", 404

    # 查詢商品所屬餐廳 ID
    restaurant_id_query = "SELECT restaurant_id FROM menu_items WHERE id = %s"
    restaurant_id = execute_query(restaurant_id_query, (item_id,), fetchone=True)
    if not restaurant_id:
        flash('無法獲取餐廳信息')
        return "無法獲取餐廳信息", 404

    # 渲染商品詳情頁面
    return render_template('cart.html', item=item, restaurant_id=restaurant_id['restaurant_id'])

#添加商品到購物車
@app.route('/add_to_cart', methods=['POST', 'GET'])
@login_required
def add_to_cart():
    if request.method == 'POST':
        item_id = int(request.form.get('item_id'))
        menu_item = checkout_items(item_id)

        if not menu_item:
            return jsonify({'success': False, 'message': '商品不存在！'}), 404

        try:
            # 獲取並驗證數量
            quantity = int(request.form.get('quantity', 1))
            item_name = menu_item['name']
            item_price = float(menu_item['price'])  # 確保是數值類型
            restaurant_id = menu_item.get('restaurant_id', 1)

            # 確保購物車存在
            if 'cart' not in session:
                session['cart'] = []

            # 檢查是否有其他家餐廳商品
            if session['cart'] and session['cart'][0]['restaurant_id'] != restaurant_id:
                return jsonify({'success': False, 'message': '購物車中已有其他餐廳的商品，請清空購物車後添加新商品！'}), 400

            # 計算總共金額
            total_price = quantity * item_price

            # 檢查購物車是否有此商品
            for item in session['cart']:
                if item['item_id'] == item_id:
                    item['quantity'] += quantity
                    item['total_price'] += total_price
                    break
            else:
                # 如果購物車沒有此商品，新增
                session['cart'].append({
                    'restaurant_id': restaurant_id,
                    'item_id': item_id,
                    'item_name': item_name,
                    'item_price': item_price,
                    'quantity': quantity,
                    'total_price': total_price
                })

            session.modified = True  # 確保 session 更新生效

            # 計算購物車總量和金額
            total_quantity = sum(item['quantity'] for item in session['cart'])
            total_amount = sum(item['total_price'] for item in session['cart'])

            return jsonify({'success': True, 'cartQuantity': total_quantity, 'cartAmount': total_amount})

        except ValueError as e:
            return jsonify({'success': False, 'message': f'數據處理錯誤: {e}'}), 400

    elif request.method == 'GET':
        # 處理 GET 請求，顯示結算頁面
        cart = session.get('cart', [])
        total_amount = sum(item['total_price'] for item in cart) if cart else 0

        # 獲取購物車第一格商品的ID，作為返回按鈕的商品ID
        default_item_id = cart[0]['item_id'] if cart else None

        return render_template('checkout.html', cart=cart, total_amount=total_amount, default_item_id=default_item_id)

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    try:
        data = request.get_json()
        item_id = int(data['item_id'])

        # 檢查購物車是否存在
        if 'cart' not in session or not session['cart']:
            return jsonify({'success': False, 'message': '購物車為空！'}), 404

        # 刪除指定商品
        session['cart'] = [item for item in session['cart'] if item['item_id'] != item_id]
        session.modified = True

        # 計算新的總金額
        total_amount = sum(item['total_price'] for item in session['cart']) if session['cart'] else 0

        return jsonify({'success': True, 'totalAmount': total_amount})
    except Exception as e:
        print(f"刪除商品失敗: {e}")
        return jsonify({'success': False, 'message': '刪除商品失敗'}), 500

@app.route('/sendorder', methods=['POST'])
@login_required
def sendorder():
    try:
        # 从 session 获取 user_id
        user_id = session.get('user_id')
        if not user_id:
            return "使用者未登入或會話已過期", 401

        # 從表單中獲取其他資料
        total_amount = float(request.form['total_amount'])
        restaurant_id = request.form['restaurant_id']
        order_items = request.form.getlist('order_items')  # 獲取訂單商品資料

        # 處理 order_items，格式：菜品名稱 x 數量
        formatted_order_items = []
        for item in order_items:
            try:
                # 解析「菜品名稱 x 數量」格式
                item_name, quantity = item.split(' x ')
                formatted_order_items.append((item_name.strip(), int(quantity)))  # 去除可能的空格並轉換為元組
            except ValueError:
                # 如果資料格式不正確，拋出異常
                raise ValueError(f"订单项格式不正确: {item}")

        # 格式化商品資料，轉換為「item_name*quantity」的字串
        formatted_order_items_str = "; ".join([f"{item[0]}*{item[1]}" for item in formatted_order_items])

        # 呼叫 Send_order 插入訂單資料，並獲取訂單號
        order_id = Send_order(
            restaurant_id=restaurant_id,
            user_id=user_id,  # 直接使用從 session 獲取的使用者 ID
            item_id_and_quantity=formatted_order_items,  # 使用元組列表
            total_price=total_amount
        )
        
        if order_id:  # 如果訂單插入成功並返回訂單號
            # 清空購物車
            session.pop('cart', None)
            return render_template('sendorder.html', order_id=order_id)
        else:
            return "訂單提交失敗，請稍後再試", 500

    except Exception as e:
        print(f"發送訂單失敗: {e}")
        return "訂單提交失敗，請稍後再試", 500
    
@app.route('/vieworders')
@login_required
def view_orders():
    """展示使用者的訂單狀態"""
    try:
        user_id = session.get('user_id')  # 確保從 session 中獲取使用者 ID
        if not user_id:
            flash("無法確定您的身份，請重新登入")
            return redirect(url_for('login'))
        
        # 調用函數獲取使用者訂單
        orders = get_user_orders(user_id)
        
        if not orders:
            flash("您沒有任何訂單")
        
        return render_template('view_orders.html', orders=orders)
    
    except Exception as e:
        print(f"獲取訂單失敗: {e}")
        flash("無法獲取訂單，請稍後再試")
        return redirect(url_for('index'))


@app.route('/complete_order/<int:order_id>', methods=['POST'])
@login_required
def complete_order(order_id):
    """標記訂單為已完成並跳轉到評價頁面"""
    try:
        # 從 session 獲取使用者 ID
        user_id = session.get('user_id')
        if not user_id:
            flash("無效的使用者身份，請重新登入")
            return redirect(url_for('login'))

        # 獲取使用者的所有訂單
        orders = get_user_orders(user_id)

        # 檢查是否存在目標訂單
        order = next((o for o in orders if o['id'] == order_id), None)
        if not order:
            flash("找不到該訂單")
            return redirect(url_for('view_orders'))

        # 從訂單中獲取 restaurant_id
        restaurant_id = order['restaurant_id']

        # 更新訂單狀態為已完成
        update_order_status(order_id, restaurant_id, 'Completed')  # 確保函數定義中參數順序正確

        # 跳轉到評價頁面
        return redirect(url_for('rate_order', order_id=order_id))

    except Exception as e:
        print(f"標記訂單完成失敗: {e}")
        flash("無法完成訂單，請稍後再試")
        return redirect(url_for('view_orders'))

@app.route('/rate_order/<int:order_id>', methods=['GET'])
@login_required
def rate_order(order_id):
    """顯示訂單評價頁面"""
    try:
        # 從 session 獲取使用者 ID
        user_id = session.get('user_id')
        if not user_id:
            flash("無效的使用者身份，請重新登入")
            return redirect(url_for('login'))

        # 獲取使用者的所有訂單
        orders = get_user_orders(user_id)

        # 查找指定訂單
        order = next((o for o in orders if o['id'] == order_id), None)
        if not order:
            flash("找不到該訂單")
            return redirect(url_for('view_orders'))

        # 渲染評價頁面
        return render_template('rate_order.html', order=order)

    except Exception as e:
        print(f"獲取訂單資訊失敗: {e}")
        flash("無法加載訂單資訊，請稍後再試")
        return redirect(url_for('view_orders'))


@app.route('/submit_review/<int:order_id>', methods=['POST'])
@login_required
def submit_review(order_id):
    """提交訂單評價"""
    try:
        # 從表單中獲取評分和評論
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        # 驗證輸入
        if not rating:
            flash("評分是必填項")
            return redirect(url_for('rate_order', order_id=order_id))
        if not comment:
            flash("請提供評論內容")
            return redirect(url_for('rate_order', order_id=order_id))

        # 驗證評分範圍
        if not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            flash("評分必須是1~5之間的數字")
            return redirect(url_for('rate_order', order_id=order_id))

        # 保存評價到數據庫
        submit_order_review(order_id, int(rating), comment)

        flash("評價提交成功，謝謝您的反饋！")
        return redirect(url_for('view_orders'))

    except Exception as e:
        print(f"提交評價失敗: {e}")
        flash("評價提交失敗，請稍後再試")
        return redirect(url_for('rate_order', order_id=order_id))

#外送員
@app.route('/rider_dashboard')
def rider_dashboard():
    rider_id = session.get('user_id')
    if not rider_id:
        return redirect(url_for('login'))
    
    # 获取所有的订单，不做任何过滤
    orders = get_rider_orders()  # 不传递任何参数，查询所有订单

    print(f"Fetched {len(orders)} orders.")  # 输出调试信息

    return render_template('rider_dashboard.html', user_id=rider_id, orders=orders)

@app.route('/available_orders')
def available_orders():
    # 获取所有的订单
    orders = get_rider_orders()  # 不传递任何参数，查询所有订单
    print(f"Fetched {len(orders)} available orders.")

    return render_template('available_orders.html', orders=orders)


@app.route('/pick_order/<int:order_id>')
def pick_order(order_id):
    # 外送员选择取餐订单
    rider_id = session.get('user_id')
    
    if rider_id:
        # 确保外送员没有重复分配相同的订单
        if not is_order_assigned(order_id):  # 检查订单是否已经被接单
            # 更新订单状态
            if assign_order_to_rider(order_id, rider_id):  # 如果成功分配订单
                flash("Order has been assigned to you successfully!", "success")  # 显示成功消息
                return redirect(url_for('available_orders'))  # 重定向回待接单页面
            else:
                flash("Error: Could not assign this order.", "danger")
                return redirect(url_for('available_orders'))
        else:
            flash("This order has already been assigned.", "danger")  # 如果订单已被接单
            return redirect(url_for('available_orders'))
    flash("Please log in to continue.")  # 若未登录显示提示
    return redirect(url_for('login'))

@app.route('/start_delivery/<int:order_id>', methods=['GET', 'POST'])
def start_delivery(order_id):
    rider_id = session.get('user_id')
    
    if rider_id:
        # 更新訂單狀態為 'On the Way'
        update_order_status_to_on_the_way(order_id, rider_id)
        flash("您已成功取餐，正在外送中！")
        return redirect(url_for('pick_up_orders'))  # 跳轉回待取餐頁面
    else:
        flash("請先登入！")
        return redirect(url_for('login'))

@app.route('/on_delivery/<int:order_id>', methods=['GET'])
def on_delivery(order_id):
    rider_id = session.get('user_id')  # 获取当前骑手的 user_id
    
    if rider_id:
        # 从 dbutils 获取该订单和骑手的关联信息
        order = dbUtils.get_order_by_id_and_rider(order_id, rider_id)
        
        if order:
            return render_template('pick_up_orders.html', order=order)  # 渲染订单详细页面
        else:
            flash("订单不存在或您没有权限查看该订单！")
            return redirect(url_for('pick_up_orders'))  # 返回待取餐订单列表页面
    else:
        flash("请先登录！")
        return redirect(url_for('login'))  # 如果没有登录，跳转到登录页面

        
@app.route('/pick_up_orders')
def pick_up_orders():
    # 获取当前登录的外送员ID
    rider_id = session.get('user_id')
    
    if rider_id:
        # 获取待取餐的订单，状态为 'picked up' 或 'On the way'
        orders = fetch_orders_by_rider(rider_id)
        
        if orders:
            return render_template('pick_up_orders.html', orders=orders)  # 渲染页面并传递订单数据
        else:
            return render_template('pick_up_orders.html', orders=[])  # 如果没有待取餐的订单，传递空列表
    else:
        flash("Please log in to continue.")  # 如果没有登录，弹出提示
        return redirect(url_for('login'))  # 重定向到登录页面

@app.route('/complete_delivery/<int:order_id>', methods=['GET'])
def complete_delivery(order_id):
    rider_id = session.get('user_id')  # 获取当前登录的外送员ID
    
    if rider_id:
        # 更新订单状态为 'Delivered'（已送达）
        update_order_status_to_delivered(order_id, rider_id)
        flash("订单已送达！")
        return redirect(url_for('pick_up_orders'))
    else:
        flash("请先登录！")
        return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)


