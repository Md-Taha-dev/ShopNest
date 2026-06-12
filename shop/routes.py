from shop import app,db
from flask import render_template,redirect, url_for, flash, request, abort
from shop.forms import SignupForm, LoginForm
from shop.models import User, Order, Cart, Product
from flask_login import login_user,logout_user, current_user


@app.route("/")
@app.route("/home")
def home_page():
    products=Product.query.all()
    return render_template('home.html',products=products)

@app.route("/search")
def search_page():
    query = request.args.get("q")
    products = Product.query.filter(Product.product_name.ilike(f"%{query}%")).all()
    return render_template("search.html",products=products,query=query)


@app.route("/login",methods=['GET','POST'])
def login_page():
    form=LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()

        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Successs! You are logged in as:{attempted_user.username}','success')
            return redirect(url_for('home_page'))
            
        else:
            flash('Username or password is incorrect! Please try again','error')
    
    return render_template('login.html',form=form)

@app.route("/signup",methods=['GET','POST'])
def signup_page():
    form= SignupForm()
    if form.validate_on_submit():
        user_to_create=User(username=form.username.data, email=form.email.data, password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for('login_page'))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'there was an error:{err_msg}', "error")

    
    return render_template('signup.html', form=form)
    

@app.route("/cart")
def cart_page():

    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    
    if not cart_items:
        return render_template("cart.html", items=[], total=0, empty=True)

    total = 0
    items = []

    for item in cart_items:
        product = Product.query.get(item.product_id)

        item_total = product.price * item.quantity
        total += item_total

        items.append({
            "product": product,
            "quantity": item.quantity,
            "item_total": item_total
        })

    return render_template("cart.html", items=items, total=total, empty=False)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!","warning")
    return redirect(url_for('home_page'))


@app.route("/profile")
def profile_page():
    return render_template('profile.html', user=current_user)

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=product_id,
            quantity=1
        )
        db.session.add(cart_item)

    db.session.commit()

    return redirect(url_for("home_page"))


@app.context_processor
def cart_count():
    if current_user.is_authenticated:
        count = db.session.query(db.func.sum(Cart.quantity)).filter_by(user_id=current_user.id).scalar()
        return dict(cart_count=count or 0)
    return dict(cart_count=0)


@app.route("/cart/increase/<int:product_id>")
def increase_quantity(product_id):

    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += 1
        db.session.commit()

    return redirect(url_for("cart_page"))

@app.route("/cart/decrease/<int:product_id>")
def decrease_quantity(product_id):

    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity -= 1

        
        if cart_item.quantity <= 0:
            db.session.delete(cart_item)
        db.session.commit()

    return redirect(url_for("cart_page"))

@app.route("/cart/remove/<int:product_id>")
def remove_item(product_id):

    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

    return redirect(url_for("cart_page"))

@app.route("/checkout")
def checkout():
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    
    if len(cart_items) == 0:
        return redirect(url_for("cart_page"))

    
    for item in cart_items:
        order = Order(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price,
            status="Pending"
        )
        db.session.add(order)

    
    Cart.query.filter_by(user_id=current_user.id).delete()

    db.session.commit()

    return redirect(url_for("orders_page"))

@app.route("/orders")
def orders_page():

    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

    orders = Order.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "orders.html",
        orders=orders,
        empty=(len(orders) == 0)
    )



@app.route("/admin")
def admin_page():
   
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

   
    if current_user.username != "admin" or current_user.email != "admin@gmail.com":
        abort(404)
    
    
    section = request.args.get('section', 'users')
    data = []

    
    if section == 'users':
        data = User.query.all()
    elif section == 'products':
        data = Product.query.all()
    elif section == 'orders':
        data = Order.query.all()

    
    return render_template("admin.html", section=section, data=data)



@app.route("/admin/add-product", methods=['POST'])
def admin_add_product():
   
    if not current_user.is_authenticated or current_user.username != "admin" or current_user.email != "admin@gmail.com":
        abort(404)
    
    
    new_product = Product(
        product_name=request.form.get('product_name'),
        price=float(request.form.get('price')),
        stock=int(request.form.get('stock')),
        picture=request.form.get('picture')
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    flash("New product added to inventory successfully!", "success")
    return redirect(url_for('admin_page', section='products'))


@app.route("/admin/update-status/<int:order_id>", methods=['POST'])
def admin_update_status(order_id):
    
    if not current_user.is_authenticated or current_user.username != "admin" or current_user.email != "admin@gmail.com":
        abort(404)
    
    
    order = Order.query.get(order_id)
    if order:
        
        order.status = request.form.get('new_status')
        db.session.commit()
        flash(f"Order #{order_id} status updated successfully!", "success")
        
    return redirect(url_for('admin_page', section='orders'))

@app.route("/admin/update-product-stock/<int:product_id>", methods=['POST'])
def admin_update_product_stock(product_id):
    
    if not current_user.is_authenticated or current_user.username != "admin" or current_user.email != "admin@gmail.com":
        abort(404)
        
    product_entry = Product.query.get(product_id)
    if product_entry:
        
        product_entry.stock = int(request.form.get('new_stock'))
        db.session.commit()
        flash(f"Inventory count updated successfully for Product ID #{product_id}!", "success")
        
    return redirect(url_for('admin_page', section='products'))



@app.route("/admin/delete-product/<int:product_id>", methods=['POST'])
def admin_delete_product(product_id):
    
    if not current_user.is_authenticated or current_user.username != "admin" or current_user.email != "admin@gmail.com":
        abort(404)
        
    product_entry = Product.query.get(product_id)
    if product_entry:
        db.session.delete(product_entry)
        db.session.commit()
        flash(f"Product ID #{product_id} has been permanently dropped from inventory registries!", "warning")
        
    return redirect(url_for('admin_page', section='products'))