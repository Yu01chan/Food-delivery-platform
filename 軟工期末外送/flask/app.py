from flask import Flask, render_template, request, session, redirect
from functools import wraps
from dbUtils import getList,add,setFinish,auction,additem,bid,cursor1,myitems,delmyitems,addprice,edititem,addregister

# creates a Flask application, specify a static folder on /
app = Flask(__name__, static_folder='static',static_url_path='/')
#set a secret key to hash cookies
app.config['SECRET_KEY'] = '123TyU%^&'

#define a function wrapper to check login session
def login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		loginID = session.get('loginID')# 從 session 中取得 'loginID'
		if not loginID:
			return redirect('/loginPage.html')
		return f(*args, **kwargs)
	return wrapper


@app.route("/getAjaxData",methods=['POST'])
#取得網址作為參數
def getdata111():
   id=request.form['userID']
   name=request.form['userName']
   return f"I got your input : {id},{name}"

@app.route("/") 
@login_required
def hello(): 
	return redirect('/auctionitems')

@app.route("/test/<string:name>/<int:id>")
#取得網址作為參數
def useParam(name,id):
	return f"got name={name}, id={id} "

@app.route("/update",methods=['POST'])
#使用server side render: template 樣板
def upd():
	name =request.form['name']
	cnt =request.form['content']
	#sql
	html=f"update===>nnn:{name},cnt:{cnt}"
	return html
    

@app.route("/edit")
#使用server side render: template 樣板
def h1():
	dat={
		"name": "大牛",
		"content":"內容說明文字"
	}
	#editform.html 存在於 templates目錄下, 將dat 作為參數送進 editform.html, 名稱為 data
	return render_template('editform.html', data=dat)

@app.route("/list")
#使用server side render: template 樣板
def h2():
	dat=[
		{
			"name": "大牛",
			"p":"愛吃瓜"
		},
		{
			"name": "小李",
			"p":"怕榴槤"
		},
		{
			"name": "",
			"p":"ttttt"
		},
		{
			"name": "老謝",
			"p":"來者不拒"
		}
	]
	return render_template('list.html', data=dat)

@app.route('/input', methods=['GET', 'POST'])
def userInput():
	if request.method == 'POST':
		form =request.form
	else:
		form= request.args

	txt = form['txt']  # pass the form field name as key
	note =form['note']
	select = form['sel']
	msg=f"method: {request.method} txt:{txt} note:{note} sel: {select}"
	return msg

@app.route("/listJob")
#使用server side render: template 樣板
def gl():
	dat=getList()
	return render_template('todolist.html', data=dat)

@app.route('/addJob', methods=['POST'])
def addJob():
	if request.method == 'POST':
		form =request.form
	else:
		form= request.args

	jobName = form['name']  # pass the form field name as key
	jobCont =form['content']
	due = form['due']
	add(jobName,jobCont,due)
	return redirect("/listJob")

@app.route('/setFinish', methods=['GET'])
def done():
	if request.method == 'POST':
		form =request.form
	else:
		form= request.args

	id = form['id']  # pass the form field name as key
	setFinish(id)
	return redirect("/listJob")


#handles login request
@app.route('/login', methods=['POST'])
def login():
    form = request.form
    user_id = form['ID']
    user_password = form['PWD']
    
    # 調用 cursor1 函數以獲取使用者資料
    user = cursor1(user_id,user_password)

	# 確認查詢結果是否存在
    if user is None:
        session['loginID'] = False  # 查詢結果為空，登入失敗
        return redirect("/loginPage.html")

    # 驗證 id/pwd
    if user['password'] == user_password:
        session['loginID'] = user['id']  # 使用使用者的 id 存入 session
        return redirect("/myitems")  # 登入成功
    else:
        session['loginID'] = False  # 登入失敗
        return redirect("/loginPage.html")  # 重新導向到登入表單

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_id = request.form['ID']
        username = request.form['username']
        password = request.form['PWD']
        created_at = request.form.get('time')  # 獲取當前時間
        
        # 呼叫 addregister 函數來插入資料
        addregister(user_id, username, password, created_at)

        return redirect("/loginPage.html")  # 註冊成功後重定向到登入頁面
    
    return render_template("register.html")  # 渲染註冊頁面


@app.route("/logout")
def logout():
    session.pop('loginID', None)  # 刪除 session 中的用戶 ID
    return redirect('/loginPage.html')  # 重定向到登錄頁面

@app.route('/myitems')
def my_items():
    user_id = session.get('loginID')  # 獲取 session 中的登入 ID
    if not user_id:
        return redirect('/loginPage.html')  # 如果未登入，重定向到登入表單

    # 調用 myitems 函數獲取商品列表
    items = myitems(user_id)
    
    # 渲染模板，並將商品數據傳遞給前端頁面
    return render_template('myitems.html', items=items)


if __name__ == "__main__":
	app.run(debug=True)
     
@app.route('/renew', methods=['POST'])
def new():
	if request.method == 'POST':
		form =request.form
	else:
		form= request.args

	item_name = form['name']  # pass the form field name as key
	description =form['due']
	base_price = form['price']
	user_id = session.get('loginID')  # 從 session 中獲取當前用戶的 loginID
	if not user_id:
		return redirect('/loginPage.html')  # 如果用戶未登入，重定向到登入頁面
	created_at = form['time']
	additem(item_name,description,base_price,user_id,created_at)
	return redirect("/myitems")

@app.route("/delete/<string:item_id>")
def delete(item_id):
    user_id = session.get('loginID')  # 獲取登錄者的 ID
    items = delmyitems(item_id, user_id)  # 傳遞用戶 ID
    return render_template('myitems.html', items=items)

@app.route('/edititem', methods=['GET', 'POST'])
def edit_item():
    item_id = request.args.get('item_id') or request.form.get('item_id')
    user_id = session.get('loginID')

    if not user_id:
        return redirect('/loginPage.html')

    if request.method == 'POST':
        item_name = request.form.get('name')
        description = request.form.get('due')
        base_price = request.form.get('price')
        created_at = request.form.get('time')

        # 執行更新操作
        edititem(item_id, item_name, description, base_price, user_id, created_at)
        return redirect("/myitems")
    else:
    # 執行查詢操作並將結果傳遞到模板
        item_data = edititem(item_id)
        return render_template("edititem.html", item=item_data)

@app.route("/auctionitems")
#使用server side render: template 樣板
def auctionitems():
	dat=auction()
	return render_template('auctionitems.html', data=dat)

@app.route("/bids")
def bids():
    # 获取传入的 item_id 参数
    item_id = request.args.get('item_id')
    dat = bid(item_id)  # 获取特定商品的竞拍记录

    # 使用字典根据 item_id 分组（如不需要分组，也可以直接返回 dat）
    grouped_bids = {}
    for record in dat:
        current_item_id = record['item_id']
        if current_item_id not in grouped_bids:
            grouped_bids[current_item_id] = []
        grouped_bids[current_item_id].append(record)

    # 如果没有竞标记录，传递一个空的分组以便在模板中显示
    if not grouped_bids:
        grouped_bids["no_bids"] = []

    return render_template('bids.html', grouped_bids=grouped_bids)

@app.route('/biditems', methods=['POST', 'GET'])  
def bid_items():
    if request.method == 'GET':
        item_id = request.args.get('item_id')
        print("Received item_id:", item_id)
        
        if not item_id:
            return "Item ID 未提供", 400  # 若無 item_id，返回錯誤信息
        
        return render_template('biditems.html', item_id=item_id)
    
    elif request.method == 'POST':
        form = request.form
        item_id = form.get('item_id')
        user_id = session.get('loginID')
        created_at = form.get('time')
        price = form.get('price')  # 從表單中提取價格

        print("Item ID:", item_id)
        print("Price:", price)
        print("User ID:", user_id)
        print("Created At:", created_at)

        if not user_id:
            return redirect('/loginPage.html')
        
        if not price or not created_at:
            return "請提供價格和時間", 400

        # 將價格轉換為浮點數
        try:
            price = float(price)
        except ValueError:
            return "價格無效", 400

        # 直接调用 addprice 函数并获取返回结果
        result = addprice(item_id, price, user_id, created_at)

        if result == "出價無效":
            # 出價失敗，回到競標頁面並顯示錯誤訊息
            return render_template("biditems.html", item_id=item_id, error="出價低於或等於最高出價或基準價格，請再試一次。")
        else :
             addprice(item_id, price, user_id, created_at)
        # 出價成功，返回到 /auctionitems 頁面
             return redirect('/auctionitems')

