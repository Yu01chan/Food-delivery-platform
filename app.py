from flask import Flask, render_template, request, session, redirect, url_for, flash
from functools import wraps
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, FloatField
from wtforms.validators import DataRequired, Length
from flask import session, redirect, url_for, request, render_template
from flask import jsonify
import os
import uuid
from dbUtils import (
    register_users, login_users, add_menu_item, get_menu_items,
    edit_menu_item, delete_menu_item, get_orders, get_order_details,
    update_order_status, notify_rider_to_pickup,
    get_menu_items_customer_data,get_menu_restaurant_data,
    cartmenu_items,checkout_items,execute_query,Send_order,insert_into_db
)

app = Flask(__name__)
app.config['SECRET_KEY'] = '123TyU%^&'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制最大上传文件为 16MB

# Utility Functions
def allowed_file(filename):
    # 使用 MIME 类型确保文件的安全性
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
            flash(f"文件上传失败: {str(e)}")
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
            flash("请先登录")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# 註冊頁面
@app.route("/users", methods=["GET", "POST"]) 
def users():
    if request.method == "POST":
        user_id = request.form['user_id']
        password = request.form['password']
        role = request.form['role']  # 獲取 role 值
        if register_users(user_id, password, role):  # 使用 register_users 函數
            flash("注册成功！请登录")
            return redirect(url_for('login'))
        else:
            flash("注册失败，账户可能已存在")
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
        else:
            flash("登录失败，请检查您的账户信息")
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

        # 上传图片并保存路径
        image_path = save_uploaded_file(image)
        if not image_path:
            flash("图片上传失败，请重新尝试！")
            return redirect(url_for("add_menu_item_route"))

        # 保存菜单项到数据库
        restaurant_id = session.get('user_id')
        if add_menu_item(name, description, price, restaurant_id, image_path):
            flash("菜单项添加成功！")
            return redirect(url_for("menu_list"))
        else:
            flash("添加菜单项失败，请稍后再试！")

    return render_template("add_menu_item.html")

@app.route("/edit_menu_item/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_menu_item_route(item_id):
    restaurant_id = session.get('user_id')
    menu_item = next(
        (item for item in get_menu_items(restaurant_id) if item['id'] == item_id), None
    )
    if not menu_item:
        flash("菜单项未找到。")
        return redirect(url_for("menu_list"))

    # 初始化表单并填充默认值
    form = MenuItemForm(
        name=menu_item.get("name"),
        description=menu_item.get("description"),
        price=menu_item.get("price")
    )

    # 当前图片路径修正，用于显示和存储
    current_image_path = menu_item.get('image_path', '').replace("\\", "/")
    display_image_path = (
        url_for('static', filename=current_image_path) if current_image_path else None
    )

    if form.validate_on_submit():
        # 处理新图片上传
        if form.image.data:
            new_image_path = save_uploaded_file(form.image.data)
            if not new_image_path:
                flash("图片上传失败，请重新尝试。")
                return redirect(url_for("edit_menu_item_route", item_id=item_id))
            current_image_path = new_image_path.replace("\\", "/")

        # 更新菜单项
        if edit_menu_item(
            item_id,
            form.name.data,
            form.description.data,
            form.price.data,
            restaurant_id,
            current_image_path
        ):
            flash("菜单项更新成功！")
            return redirect(url_for("menu_list"))

        flash("更新菜单项失败。")

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
        flash("菜单项删除成功！")
    else:
        flash("删除菜单项失败。")
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
    return render_template("order_details.html", order=order, order_items=order_items)

@app.route("/update_order_status/<int:order_id>", methods=["POST"])
@login_required
def update_order_status_route(order_id):
    new_status = request.form['status']
    restaurant_id = session.get('user_id')
    if update_order_status(order_id, new_status, restaurant_id):
        flash("订单状态更新成功！")
    else:
        flash("更新订单状态失败。")
    return redirect(url_for("orders"))

@app.route("/notify_rider/<int:order_id>", methods=["POST"])
@login_required
def notify_rider(order_id):
    restaurant_id = session.get('user_id')
    if notify_rider_to_pickup(order_id, restaurant_id):
        flash("骑手已被通知去取餐。")
    else:
        flash("通知骑手失败。")
    return redirect(url_for("orders"))

@app.route("/logout")
@login_required
def logout():
    session.pop('user_id', None)
    flash("已注销，欢迎再次登录！")
    return redirect(url_for('login'))

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
    # 获取指定餐厅的菜单项
    menu_items = get_menu_restaurant_data(restaurant_id)

    # 确保图片路径为有效的静态资源
    for item in menu_items:
        if item.get('image_path'):
            # 确保图片路径相对于静态文件夹
            item['image_path'] = item['image_path'].replace("\\", "/")

    return render_template("ordermenu.html", menu_items=menu_items)

# 查看购物车商品详情
@app.route('/cart_item/<int:item_id>', methods=['GET'])
@login_required
def view_cart_item(item_id):
    # 获取商品信息
    item = cartmenu_items(item_id)
    if not item:
        flash('商品未找到')
        return "商品未找到", 404

    # 查询商品所属的餐厅 ID
    restaurant_id_query = "SELECT restaurant_id FROM menu_items WHERE id = %s"
    restaurant_id = execute_query(restaurant_id_query, (item_id,), fetchone=True)
    if not restaurant_id:
        flash('无法获取餐厅信息')
        return "无法获取餐厅信息", 404

    # 渲染商品详情页面
    return render_template('cart.html', item=item, restaurant_id=restaurant_id['restaurant_id'])

# 添加商品到购物车
@app.route('/add_to_cart', methods=['POST', 'GET'])
@login_required
def add_to_cart():
    if request.method == 'POST':
        item_id = int(request.form.get('item_id'))
        menu_item = checkout_items(item_id)

        if not menu_item:
            return jsonify({'success': False, 'message': '商品不存在！'}), 404

        try:
            # 获取并验证数量
            quantity = int(request.form.get('quantity', 1))
            item_name = menu_item['name']
            item_price = float(menu_item['price'])  # 确保是数值类型
            restaurant_id = menu_item.get('restaurant_id', 1)

            # 确保购物车存在
            if 'cart' not in session:
                session['cart'] = []

            # 检查是否有其他餐厅的商品
            if session['cart'] and session['cart'][0]['restaurant_id'] != restaurant_id:
                return jsonify({'success': False, 'message': '购物车中已有其他餐厅的商品，请清空购物车后添加新商品！'}), 400

            # 计算小计
            total_price = quantity * item_price

            # 检查购物车是否已有此商品
            for item in session['cart']:
                if item['item_id'] == item_id:
                    item['quantity'] += quantity
                    item['total_price'] += total_price
                    break
            else:
                # 如果购物车中没有此商品，新增
                session['cart'].append({
                    'restaurant_id': restaurant_id,
                    'item_id': item_id,
                    'item_name': item_name,
                    'item_price': item_price,
                    'quantity': quantity,
                    'total_price': total_price
                })

            session.modified = True  # 确保 session 更新生效

            # 计算购物车总量和总金额
            total_quantity = sum(item['quantity'] for item in session['cart'])
            total_amount = sum(item['total_price'] for item in session['cart'])

            return jsonify({'success': True, 'cartQuantity': total_quantity, 'cartAmount': total_amount})

        except ValueError as e:
            return jsonify({'success': False, 'message': f'数据处理错误: {e}'}), 400

    elif request.method == 'GET':
        # 处理 GET 请求，显示结算页面
        cart = session.get('cart', [])
        total_amount = sum(item['total_price'] for item in cart) if cart else 0

        # 获取购物车中第一个商品的 ID，作为返回按钮的默认 ID
        default_item_id = cart[0]['item_id'] if cart else None

        return render_template('checkout.html', cart=cart, total_amount=total_amount, default_item_id=default_item_id)

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    try:
        data = request.get_json()
        item_id = int(data['item_id'])

        # 检查购物车是否存在
        if 'cart' not in session or not session['cart']:
            return jsonify({'success': False, 'message': '购物车为空！'}), 404

        # 删除指定商品
        session['cart'] = [item for item in session['cart'] if item['item_id'] != item_id]
        session.modified = True

        # 计算新的总金额
        total_amount = sum(item['total_price'] for item in session['cart']) if session['cart'] else 0

        return jsonify({'success': True, 'totalAmount': total_amount})
    except Exception as e:
        print(f"删除商品失败: {e}")
        return jsonify({'success': False, 'message': '删除商品失败'}), 500

@app.route('/sendorder', methods=['POST'])
@login_required
def sendorder():
    try:
        # 从表单中获取数据
        user_id = request.form['user_id']
        total_amount = float(request.form['total_amount'])
        restaurant_id = int(request.form['restaurant_id'])
        order_items = request.form.getlist('order_items')  # 获取订单商品数据

        # 处理 order_items，格式：菜品名称 x 数量
        formatted_order_items = []
        for item in order_items:
            try:
                # 解析 "菜品名称 x 数量" 格式
                item_name, quantity = item.split(' x ')
                formatted_order_items.append((item_name.strip(), int(quantity)))  # 去除可能的空格并转换为元组
            except ValueError:
                # 如果数据格式不正确，抛出异常
                raise ValueError(f"订单项格式不正确: {item}")

        # 格式化商品数据，转换为 "item_name&quantity" 的字符串
        formatted_order_items_str = "; ".join([f"{item[0]}&{item[1]}" for item in formatted_order_items])

        # 调用 Send_order 插入订单数据，并获取订单号
        order_id = Send_order(
            restaurant_id=restaurant_id,
            user_id=user_id,
            item_id_and_quantity=formatted_order_items,  # 使用元组列表
            total_price=total_amount
        )
        
        if order_id:  # 如果订单插入成功并返回订单号
            # 清空购物车
            session.pop('cart', None)
            return render_template('sendorder.html', order_id=order_id)
        else:
            return "订单提交失败，请稍后再试", 500

    except Exception as e:
        print(f"发送订单失败: {e}")
        return "订单提交失败，请稍后再试", 500



    
@app.route('/comment')
@login_required
def comment():
    return render_template('comment.html')




















