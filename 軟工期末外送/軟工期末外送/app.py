from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pymysql

app = Flask(__name__)
app.secret_key = 'supersecretkey'
bcrypt = Bcrypt(app)

# 資料庫連線
db = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    database='delivery_platform',
    cursorclass=pymysql.cursors.DictCursor
)

# 登錄系統配置
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# 使用者類別
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    @staticmethod
    def get(user_id):
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data['id'], user_data['username'], user_data['role'])
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# 登錄頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username'], user['role']))
            flash('登錄成功', 'success')
            if user['role'] == 'customer':
                return redirect(url_for('customer_dashboard'))
            elif user['role'] == 'restaurant':
                return redirect(url_for('restaurant_dashboard'))
            elif user['role'] == 'rider':
                return redirect(url_for('rider_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('帳號或密碼錯誤', 'error')
    return render_template('login.html')


# 登出功能
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('成功登出', 'success')
    return redirect(url_for('login'))


# 客戶功能
@app.route('/customer/dashboard', methods=['GET', 'POST'])
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        return redirect(url_for('login'))

    with db.cursor() as cursor:
        # 獲取所有餐廳及其菜單
        cursor.execute("SELECT * FROM restaurants")
        restaurants = cursor.fetchall()

    if request.method == 'POST':
        restaurant_id = request.form['restaurant_id']
        order_items = request.form.getlist('order_items')  # [menu_item_id1, menu_item_id2, ...]
        quantities = request.form.getlist('quantities')    # [quantity1, quantity2, ...]

        total_price = 0
        with db.cursor() as cursor:
            # 新增訂單
            cursor.execute("INSERT INTO orders (customer_id, restaurant_id, total_price) VALUES (%s, %s, %s)",
                           (current_user.id, restaurant_id, total_price))
            order_id = cursor.lastrowid

            # 新增訂單項目
            for i in range(len(order_items)):
                menu_item_id = order_items[i]
                quantity = int(quantities[i])
                cursor.execute("SELECT price FROM menu_items WHERE id = %s", (menu_item_id,))
                price = cursor.fetchone()['price']
                total_price += price * quantity

                cursor.execute("INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%s, %s, %s)",
                               (order_id, menu_item_id, quantity))

            # 更新訂單總金額
            cursor.execute("UPDATE orders SET total_price = %s WHERE id = %s", (total_price, order_id))
            db.commit()

        flash('訂單已提交！', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('customer_dashboard.html', restaurants=restaurants)


# 餐廳功能
@app.route('/restaurant/dashboard', methods=['GET', 'POST'])
@login_required
def restaurant_dashboard():
    if current_user.role != 'restaurant':
        return redirect(url_for('login'))

    with db.cursor() as cursor:
        # 獲取餐廳的菜單
        cursor.execute("SELECT * FROM menu_items WHERE restaurant_id = %s", (current_user.id,))
        menu_items = cursor.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']

        with db.cursor() as cursor:
            cursor.execute("INSERT INTO menu_items (restaurant_id, name, price) VALUES (%s, %s, %s)",
                           (current_user.id, name, price))
            db.commit()

        flash('餐點新增成功！', 'success')
        return redirect(url_for('restaurant_dashboard'))

    return render_template('restaurant_dashboard.html', menu_items=menu_items)


# 外送員功能
@app.route('/rider/dashboard', methods=['GET', 'POST'])
@login_required
def rider_dashboard():
    if current_user.role != 'rider':
        return redirect(url_for('login'))

    with db.cursor() as cursor:
        cursor.execute("""
            SELECT o.id, u.username AS customer_name, r.name AS restaurant_name, o.total_price, o.status
            FROM orders o
            JOIN users u ON o.customer_id = u.id
            JOIN restaurants r ON o.restaurant_id = r.id
            WHERE o.status IN ('pending', 'in_progress')
        """)
        orders = cursor.fetchall()

    return render_template('delivery.html', orders=orders)


# 平台管理功能
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('login'))

    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

    return render_template('admin_dashboard.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)