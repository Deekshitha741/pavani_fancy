from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sripavani-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sripavani.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ── Set your WhatsApp number here (country code + number, no + or spaces) ──
ADMIN_WHATSAPP_NUMBER = '919392964427'  # e.g. 919876543210

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -----------------------------------------
# MODELS
# -----------------------------------------

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(150), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    phone         = db.Column(db.String(20))
    dob           = db.Column(db.String(20))
    gender        = db.Column(db.String(10))
    address       = db.Column(db.Text)
    city          = db.Column(db.String(100))
    state         = db.Column(db.String(100))
    pincode       = db.Column(db.String(10))
    password_hash = db.Column(db.String(256))
    is_admin      = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    cart_items    = db.relationship('CartItem', backref='user', lazy=True)
    orders        = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    image       = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_active   = db.Column(db.Boolean, default=True)
    products    = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(200), nullable=False)
    description       = db.Column(db.Text)
    price             = db.Column(db.Float, nullable=False)
    weight            = db.Column(db.Float)
    image             = db.Column(db.String(200))
    category_id       = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    is_new_collection = db.Column(db.Boolean, default=False)
    is_best_seller    = db.Column(db.Boolean, default=False)
    is_stock_out      = db.Column(db.Boolean, default=False)
    is_active         = db.Column(db.Boolean, default=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

class Offer(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200))
    subtitle    = db.Column(db.String(200))
    image       = db.Column(db.String(200))
    height_size = db.Column(db.String(20), default='medium')
    is_active   = db.Column(db.Boolean, default=True)
    sort_order  = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    product    = db.relationship('Product')

class Order(db.Model):
    id                 = db.Column(db.Integer, primary_key=True)
    user_id            = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number       = db.Column(db.String(20), unique=True, nullable=False)
    total              = db.Column(db.Float, nullable=False)
    payment_method     = db.Column(db.String(30), nullable=False)
    status             = db.Column(db.String(20), default='pending')
    delivery_name      = db.Column(db.String(150))
    delivery_phone     = db.Column(db.String(20))
    delivery_address   = db.Column(db.Text)
    delivery_city      = db.Column(db.String(100))
    delivery_state     = db.Column(db.String(100))
    delivery_pincode   = db.Column(db.String(10))
    estimated_delivery = db.Column(db.String(100), default='5-7 business days')
    admin_note         = db.Column(db.Text)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)
    items              = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    order_id      = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id    = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name  = db.Column(db.String(200))
    product_image = db.Column(db.String(200))
    price         = db.Column(db.Float)
    quantity      = db.Column(db.Integer)
    product       = db.relationship('Product')

# -----------------------------------------
# HELPERS
# -----------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, subfolder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(path, exist_ok=True)
        file.save(os.path.join(path, filename))
        return f'uploads/{subfolder}/{filename}'
    return None

def cart_count():
    if current_user.is_authenticated:
        return CartItem.query.filter_by(user_id=current_user.id).count()
    return 0

app.jinja_env.globals.update(cart_count=cart_count)

OFFER_HEIGHT_MAP = {'small': 180, 'medium': 280, 'large': 380, 'banner': 480}
app.jinja_env.globals.update(offer_height_map=OFFER_HEIGHT_MAP)

PAYMENT_LABELS = {
    'upi':        'UPI Payment',
    'netbanking': 'Net Banking',
    'card':       'Credit / Debit Card',
    'cod':        'Cash on Delivery',
}
app.jinja_env.globals.update(payment_labels=PAYMENT_LABELS)

STATUS_COLORS = {
    'pending':   ('rgba(255,183,77,.18)',  '#ffb74d'),
    'confirmed': ('rgba(79,195,247,.18)',  '#4fc3f7'),
    'shipped':   ('rgba(186,104,200,.18)', '#ba68c8'),
    'delivered': ('rgba(76,175,80,.18)',   '#66bb6a'),
    'cancelled': ('rgba(229,115,115,.18)', '#ef5350'),
}
app.jinja_env.globals.update(status_colors=STATUS_COLORS)

def generate_order_number():
    prefix = 'SP' + datetime.now().strftime('%Y%m%d')
    last = Order.query.order_by(Order.id.desc()).first()
    seq = (last.id + 1) if last else 1
    return f'{prefix}-{seq:04d}'

def build_whatsapp_url(order, user):
    """
    Builds a WhatsApp click-to-chat URL for admin notification.
    FIX: Uses urllib.parse.quote with safe='' so all special characters
    (newlines, spaces, punctuation) are properly percent-encoded for wa.me links.
    """
    items_text = ', '.join(f"{i.product_name} x{i.quantity}" for i in order.items)
    pay_label  = PAYMENT_LABELS.get(order.payment_method, order.payment_method)
    msg = (
        f"NEW ORDER - Sri Pavani Jewellery\n\n"
        f"Order#: {order.order_number}\n"
        f"Customer: {user.name}\n"
        f"Phone: {user.phone or 'N/A'}\n"
        f"Items: {items_text}\n"
        f"Total: Rs.{order.total:.0f}\n"
        f"Payment: {pay_label}\n"
        f"Ship to: {order.delivery_address}, {order.delivery_city}, "
        f"{order.delivery_state} - {order.delivery_pincode}\n\n"
        f"Please visit admin panel to process the order."
    )
    # Use quote with safe='' so newlines and all special chars are encoded
    encoded = urllib.parse.quote(msg, safe='')
    return f"https://wa.me/{ADMIN_WHATSAPP_NUMBER}?text={encoded}"

# -----------------------------------------
# MAIN ROUTES
# -----------------------------------------

@app.route('/')
def index():
    categories = Category.query.filter_by(is_active=True).all()
    all_active_offers = Offer.query.filter_by(is_active=True).order_by(Offer.sort_order, Offer.created_at).all()
    main_offers  = all_active_offers[:3]
    extra_offers = all_active_offers[3:]
    new_collections = Product.query.filter_by(is_new_collection=True, is_active=True, is_stock_out=False).limit(8).all()
    best_sellers    = Product.query.filter_by(is_best_seller=True,    is_active=True, is_stock_out=False).limit(8).all()
    all_products    = Product.query.filter_by(is_active=True, is_stock_out=False).limit(8).all()
    return render_template('index.html', categories=categories,
                           main_offers=main_offers, extra_offers=extra_offers,
                           new_collections=new_collections, best_sellers=best_sellers,
                           all_products=all_products)

@app.route('/category/<int:category_id>')
def category_page(category_id):
    cat = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id, is_active=True).all()
    other_cats = Category.query.filter(Category.id != category_id, Category.is_active == True).limit(6).all()
    return render_template('category.html', category=cat, products=products, other_categories=other_cats)

@app.route('/all-products')
def all_products():
    products   = Product.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('all_products.html', products=products, categories=categories)

# -----------------------------------------
# AUTH
# -----------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name  = request.form.get('name')
        email = request.form.get('email')
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        user = User(name=name, email=email, phone=request.form.get('phone'),
                    dob=request.form.get('dob'), gender=request.form.get('gender'),
                    address=request.form.get('address'), city=request.form.get('city'),
                    state=request.form.get('state'), pincode=request.form.get('pincode'))
        user.set_password(request.form.get('password'))
        db.session.add(user); db.session.commit()
        login_user(user)
        flash('Welcome to Sri Pavani Jewellery!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# -----------------------------------------
# PROFILE
# -----------------------------------------

@app.route('/profile')
@login_required
def profile():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total      = sum(i.product.price * i.quantity for i in cart_items)
    orders     = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', cart_items=cart_items, total=total, orders=orders)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.name    = request.form.get('name')
        current_user.phone   = request.form.get('phone')
        current_user.dob     = request.form.get('dob')
        current_user.gender  = request.form.get('gender')
        current_user.address = request.form.get('address')
        current_user.city    = request.form.get('city')
        current_user.state   = request.form.get('state')
        current_user.pincode = request.form.get('pincode')
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html')

# -----------------------------------------
# CANCEL ORDER (customer)
# -----------------------------------------

@app.route('/order/cancel', methods=['POST'])
@login_required
def cancel_order():
    order_id = request.form.get('order_id')
    order = Order.query.get_or_404(order_id)

    # Security: only the owner can cancel
    if order.user_id != current_user.id:
        flash('Unauthorised action.', 'error')
        return redirect(url_for('profile'))

    # Only allow cancellation before shipping
    if order.status in ('pending', 'confirmed'):
        order.status = 'cancelled'
        db.session.commit()
        flash(f'Order {order.order_number} has been cancelled.', 'success')
    elif order.status == 'shipped':
        flash('Your order has already been shipped and cannot be cancelled.', 'error')
    elif order.status == 'delivered':
        flash('This order has already been delivered.', 'error')
    elif order.status == 'cancelled':
        flash('This order is already cancelled.', 'error')
    else:
        flash('Unable to cancel this order.', 'error')

    return redirect(url_for('profile'))

# -----------------------------------------
# CART
# -----------------------------------------

@app.route('/cart/state')
@login_required
def cart_state():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    return jsonify({'items': [
        {'product_id': i.product_id, 'item_id': i.id, 'quantity': i.quantity} for i in items
    ]})

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.is_stock_out:
        return jsonify({'success': False, 'message': 'Out of stock'})
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id)
        db.session.add(item)
    db.session.commit()
    item  = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': count, 'item_id': item.id, 'quantity': item.quantity})

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    action = request.form.get('action')
    item   = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return jsonify({'success': False})
    if action == 'increase':
        item.quantity += 1; db.session.commit()
        return jsonify({'success': True, 'quantity': item.quantity, 'removed': False})
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1; db.session.commit()
            return jsonify({'success': True, 'quantity': item.quantity, 'removed': False})
        else:
            db.session.delete(item); db.session.commit()
            return jsonify({'success': True, 'removed': True})
    return jsonify({'success': False})

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item); db.session.commit()
    return redirect(url_for('profile'))

# -----------------------------------------
# CHECKOUT
# -----------------------------------------

@app.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total      = sum(i.product.price * i.quantity for i in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/checkout/update-address', methods=['POST'])
@login_required
def update_delivery_address():
    current_user.name    = request.form.get('name', current_user.name)
    current_user.phone   = request.form.get('phone', current_user.phone)
    current_user.address = request.form.get('address', current_user.address)
    current_user.city    = request.form.get('city', current_user.city)
    current_user.state   = request.form.get('state', current_user.state)
    current_user.pincode = request.form.get('pincode', current_user.pincode)
    db.session.commit()
    flash('Delivery address updated!', 'success')
    return redirect(url_for('checkout'))

@app.route('/checkout/place-order', methods=['POST'])
@login_required
def place_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('index'))

    total          = sum(i.product.price * i.quantity for i in cart_items)
    payment_method = request.form.get('payment_method', 'upi')

    order = Order(
        user_id          = current_user.id,
        order_number     = generate_order_number(),
        total            = total,
        payment_method   = payment_method,
        status           = 'pending',
        delivery_name    = current_user.name,
        delivery_phone   = current_user.phone or '',
        delivery_address = current_user.address or '',
        delivery_city    = current_user.city or '',
        delivery_state   = current_user.state or '',
        delivery_pincode = current_user.pincode or '',
        estimated_delivery = '5-7 business days',
    )
    db.session.add(order)
    db.session.flush()

    for ci in cart_items:
        db.session.add(OrderItem(
            order_id      = order.id,
            product_id    = ci.product_id,
            product_name  = ci.product.name,
            product_image = ci.product.image,
            price         = ci.product.price,
            quantity      = ci.quantity,
        ))
        db.session.delete(ci)

    db.session.commit()

    # ── WhatsApp Admin Notification ──
    wa_url = None
    try:
        wa_url = build_whatsapp_url(order, current_user)
        print(f"\n{'='*60}")
        print(f"WhatsApp Admin Notification URL:")
        print(wa_url)
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"WhatsApp build error: {e}")

    return render_template('order_success.html',
                           order=order, total=total,
                           payment_method=payment_method,
                           wa_url=wa_url)

# -----------------------------------------
# ADMIN helpers
# -----------------------------------------

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# -----------------------------------------
# ADMIN dashboard
# -----------------------------------------

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_products   = Product.query.count()
    total_users      = User.query.filter_by(is_admin=False).count()
    total_categories = Category.query.count()
    total_offers     = Offer.query.count()
    total_orders     = Order.query.count()
    pending_orders   = Order.query.filter_by(status='pending').count()
    recent_orders    = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_users     = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           total_products=total_products, total_users=total_users,
                           total_categories=total_categories, total_offers=total_offers,
                           total_orders=total_orders, pending_orders=pending_orders,
                           recent_orders=recent_orders, recent_users=recent_users)

# -----------------------------------------
# ADMIN orders
# -----------------------------------------

@app.route('/admin/orders', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_orders():
    if request.method == 'POST':
        action   = request.form.get('action')
        order_id = request.form.get('order_id')
        order    = Order.query.get(order_id)
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('admin_orders'))

        if action == 'update_status':
            order.status = request.form.get('status', order.status)
            db.session.commit()
            flash(f'Order #{order.order_number} status updated to "{order.status}".', 'success')

        elif action == 'set_delivery':
            preset = request.form.get('delivery_preset', '')
            custom = request.form.get('custom_delivery', '').strip()
            if preset == 'custom' and custom:
                order.estimated_delivery = custom
            elif preset and preset != 'custom':
                order.estimated_delivery = preset
            note = request.form.get('admin_note', '').strip()
            if note:
                order.admin_note = note
            db.session.commit()
            flash(f'Delivery details updated for #{order.order_number}.', 'success')

        return redirect(url_for('admin_orders'))

    status_filter = request.args.get('status', '')
    q = Order.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    orders = q.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders,
                           status_filter=status_filter)

@app.route('/admin/orders/<int:order_id>')
@login_required
@admin_required
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

# -----------------------------------------
# ADMIN categories / products / offers / customers
# -----------------------------------------

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_categories():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            image_file = request.files.get('image')
            cat = Category(name=request.form.get('name'),
                           description=request.form.get('description'),
                           image=save_file(image_file, 'categories') if image_file else None)
            db.session.add(cat); db.session.commit(); flash('Category added!', 'success')
        elif action == 'delete':
            cat = Category.query.get(request.form.get('category_id'))
            if cat:
                product_count = Product.query.filter_by(category_id=cat.id).count()
                if product_count > 0:
                    flash(f'Cannot delete "{cat.name}" — it has {product_count} product{"s" if product_count != 1 else ""} linked to it. Please delete or move those products first.', 'error')
                else:
                    db.session.delete(cat)
                    db.session.commit()
                    flash(f'Category "{cat.name}" deleted successfully.', 'success')
        elif action == 'toggle':
            cat = Category.query.get(request.form.get('category_id'))
            if cat: cat.is_active = not cat.is_active; db.session.commit()
    return render_template('admin/categories.html', categories=Category.query.all())

@app.route('/admin/products', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_products():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            price  = float(request.form.get('price', 0))
            weight = float(request.form.get('weight', 1))
            cropped_data = request.form.get('cropped_image_data')
            image_path   = None
            if cropped_data and cropped_data.startswith('data:image'):
                import base64, re
                match = re.match(r'data:image/(\w+);base64,(.*)', cropped_data, re.DOTALL)
                if match:
                    ext = match.group(1); img_data = base64.b64decode(match.group(2))
                    ts  = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    fn  = f'{ts}cropped.{ext}'
                    path = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
                    os.makedirs(path, exist_ok=True)
                    with open(os.path.join(path, fn), 'wb') as fw: fw.write(img_data)
                    image_path = f'uploads/products/{fn}'
            else:
                image_file = request.files.get('image')
                image_path = save_file(image_file, 'products') if image_file else None
            p = Product(name=request.form.get('name'), description=request.form.get('description'),
                        price=price, weight=weight, category_id=request.form.get('category_id'),
                        image=image_path,
                        is_new_collection='is_new_collection' in request.form,
                        is_best_seller='is_best_seller' in request.form)
            db.session.add(p); db.session.commit(); flash('Product added!', 'success')
        elif action == 'delete':
            p = Product.query.get(request.form.get('product_id'))
            if p: db.session.delete(p); db.session.commit(); flash('Product removed!', 'success')
        elif action == 'toggle_stock':
            p = Product.query.get(request.form.get('product_id'))
            if p: p.is_stock_out = not p.is_stock_out; db.session.commit()
    products   = Product.query.all()
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/offers', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_offers():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            image_file = request.files.get('image')
            offer = Offer(title=request.form.get('title'), subtitle=request.form.get('subtitle'),
                          image=save_file(image_file, 'offers') if image_file else None,
                          height_size=request.form.get('height_size', 'medium'),
                          sort_order=int(request.form.get('sort_order', 0)))
            db.session.add(offer); db.session.commit()
            active_count = Offer.query.filter_by(is_active=True).count()
            flash('Offer added!' + (' (4+ offers — extras go to More Deals section)' if active_count > 3 else ''), 'success')
        elif action == 'delete':
            o = Offer.query.get(request.form.get('offer_id'))
            if o: db.session.delete(o); db.session.commit(); flash('Offer removed!', 'success')
        elif action == 'toggle':
            o = Offer.query.get(request.form.get('offer_id'))
            if o: o.is_active = not o.is_active; db.session.commit()
        elif action == 'update_size':
            o  = Offer.query.get(request.form.get('offer_id'))
            ns = request.form.get('height_size')
            if o and ns in OFFER_HEIGHT_MAP: o.height_size = ns; db.session.commit(); flash('Size updated!', 'success')
    offers = Offer.query.order_by(Offer.sort_order, Offer.created_at).all()
    return render_template('admin/offers.html', offers=offers, height_map=OFFER_HEIGHT_MAP)

@app.route('/admin/customers')
@login_required
@admin_required
def admin_customers():
    customers = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/customers.html', customers=customers)

# -----------------------------------------
# INIT DB & SEED
# -----------------------------------------

def seed_data():
    if User.query.filter_by(is_admin=True).first():
        return
    admin = User(name='Admin', email='admin@sripavani.com', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)
    cats = [
        Category(name='Necklaces',  description='Elegant gold necklaces'),
        Category(name='Bangles',    description='Traditional gold bangles'),
        Category(name='Earrings',   description='Beautiful gold earrings'),
        Category(name='Rings',      description='Stunning gold rings'),
        Category(name='Chains',     description='Classic gold chains'),
        Category(name='Pendants',   description='Gorgeous gold pendants'),
    ]
    for c in cats: db.session.add(c)
    db.session.commit()
    prods = [
        Product(name='Classic Gold Necklace',  description='Elegant 1g gold necklace', price=5999, weight=1, category_id=1, is_best_seller=True),
        Product(name='Temple Bangle Set',       description='Traditional temple bangles', price=7499, weight=1, category_id=2, is_new_collection=True),
        Product(name='Jhumka Earrings',         description='Classic jhumka gold earrings', price=4299, weight=1, category_id=3, is_best_seller=True),
        Product(name='Diamond Cut Ring',        description='Beautiful diamond-cut ring', price=3999, weight=1, category_id=4, is_new_collection=True),
        Product(name='Rope Chain',              description='Elegant rope gold chain', price=5499, weight=1, category_id=5, is_best_seller=True),
        Product(name='Lakshmi Pendant',         description='Auspicious Lakshmi pendant', price=2999, weight=1, category_id=6, is_new_collection=True),
        Product(name='Choker Necklace',         description='Stunning gold choker', price=8999, weight=1, category_id=1),
        Product(name='Kada Bangle',             description='Bold gold kada bangle', price=6799, weight=1, category_id=2),
    ]
    for p in prods: db.session.add(p)
    db.session.add(Offer(title='Grand Diwali Sale', subtitle='Up to 30% off on all jewellery', is_active=True, height_size='medium'))
    db.session.commit()

with app.app_context():
    db.create_all()
    for sql in [
        "ALTER TABLE offer ADD COLUMN height_size VARCHAR(20) DEFAULT 'medium'",
        "ALTER TABLE offer ADD COLUMN sort_order INTEGER DEFAULT 0",
        "ALTER TABLE \"order\" ADD COLUMN estimated_delivery VARCHAR(100) DEFAULT '5-7 business days'",
        "ALTER TABLE \"order\" ADD COLUMN admin_note TEXT",
    ]:
        try:
            db.session.execute(db.text(sql)); db.session.commit()
        except:
            pass
    seed_data()

if __name__ == '__main__':
    app.run(debug=True)