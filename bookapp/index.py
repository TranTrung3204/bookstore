from flask import render_template, Flask
from flask import request, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user
import cloudinary.uploader
from bookapp import app, utils,login
from bookapp.models import UserRole


@app.route("/")
def index():
    kw = request.args.get('kw')
    prods = utils.load_books(kw)
    return render_template('index.html', products=prods)


@app.route("/register", methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None
        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                utils.add_user(name=name, username=username, password=password, email=email, avatar=avatar_path)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'passwords do not match'
        except Exception as ex:
            err_msg = "404 not found" + str(ex)

    return render_template('register.html', err_msg=err_msg)


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route("/user-login", methods=['get', 'post'])
def user_signin():
    err_msg = ""
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect(url_for('index'))
        else:
            err_msg = 'Username or password is incorrect !!!'
    return render_template('login.html', err_msg=err_msg)

@app.route('/admin-login', methods=['post'])
def admin_login():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = utils.check_login(username=username, password=password, user_role=UserRole.ADMIN)

    if user:
        login_user(user=user)
        return redirect('/admin')


@app.route("/user-logout")
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route('/cart')
def cart():
    err_msg = ""
    return render_template('cart.html',
                           err_msg=err_msg,
                           stats=utils.count_cart(session.get('cart')))


@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    cart = session.get('cart')
    if not cart:
        cart = {}
    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1
        }
    session['cart'] = cart

    return jsonify(utils.count_cart(cart))

@app.context_processor
def common_response():
    return {
        'categories': utils.load_book_categories(),
        'cart_stats': utils.count_cart(session.get('cart',{}))
    }


@app.route('/api/pay', methods=['post'])
def pay():
    try:
        utils.add_receipt(session.get('cart'))
        del session['cart']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/all-product')
def product_list():
    err_msg = ""
    products = utils.load_books()
    return render_template('product_list.html',
                           err_msg=err_msg,
                           products=products,
                           stats=utils.count_cart(session.get('cart')))



if __name__ == '__main__':
    from bookapp.admin import *
    app.run(debug=True)
