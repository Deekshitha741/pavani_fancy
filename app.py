from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sripavani-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sripavani.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    dob = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float)  # in grams
    image = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    is_new_collection = db.Column(db.Boolean, default=False)
    is_best_seller = db.Column(db.Boolean, default=False)
    is_stock_out = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(200))
    image = db.Column(db.String(200))
    # height options: 'small'=180px, 'medium'=280px, 'large'=380px, 'banner'=480px
    height_size = db.Column(db.String(20), default='medium')
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

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

# Height size map for offers
OFFER_HEIGHT_MAP = {
    'small': 180,
    'medium': 280,
    'large': 380,
    'banner': 480
}
app.jinja_env.globals.update(offer_height_map=OFFER_HEIGHT_MAP)

# ─────────────────────────────────────────
# MAIN ROUTES
# ─────────────────────────────────────────

@app.route('/')
def index():
    categories = Category.query.filter_by(is_active=True).all()
    all_active_offers = Offer.query.filter_by(is_active=True).order_by(Offer.sort_order, Offer.created_at).all()
    # First 3 go in main section, rest go in secondary section
    main_offers = all_active_offers[:3]
    extra_offers = all_active_offers[3:]
    new_collections = Product.query.filter_by(is_new_collection=True, is_active=True, is_stock_out=False).limit(8).all()
    best_sellers = Product.query.filter_by(is_best_seller=True, is_active=True, is_stock_out=False).limit(8).all()
    all_products = Product.query.filter_by(is_active=True, is_stock_out=False).limit(8).all()
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
    products = Product.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('all_products.html', products=products, categories=categories)

# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        user = User(name=name, email=email, phone=phone, dob=dob, gender=gender,
                    address=address, city=city, state=state, pincode=pincode)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Welcome to Sri Pavani Jewellery!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('profile.html', cart_items=cart_items, total=total)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        current_user.dob = request.form.get('dob')
        current_user.gender = request.form.get('gender')
        current_user.address = request.form.get('address')
        current_user.city = request.form.get('city')
        current_user.state = request.form.get('state')
        current_user.pincode = request.form.get('pincode')
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html')

# ─────────────────────────────────────────
# CART ROUTES
# ─────────────────────────────────────────

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
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(item)
    db.session.commit()
    # Re-fetch to get id
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': count, 'item_id': item.id, 'quantity': item.quantity})

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    action = request.form.get('action')
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return jsonify({'success': False})
    if action == 'increase':
        item.quantity += 1
        db.session.commit()
        return jsonify({'success': True, 'quantity': item.quantity, 'removed': False})
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            db.session.commit()
            return jsonify({'success': True, 'quantity': item.quantity, 'removed': False})
        else:
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'removed': True})
    return jsonify({'success': False})

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('profile'))

# ─────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_products = Product.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    total_categories = Category.query.count()
    total_offers = Offer.query.count()
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', total_products=total_products,
                           total_users=total_users, total_categories=total_categories,
                           total_offers=total_offers, recent_users=recent_users)

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_categories():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name')
            description = request.form.get('description')
            image_file = request.files.get('image')
            image_path = save_file(image_file, 'categories') if image_file else None
            cat = Category(name=name, description=description, image=image_path)
            db.session.add(cat)
            db.session.commit()
            flash('Category added!', 'success')
        elif action == 'delete':
            cat_id = request.form.get('category_id')
            cat = Category.query.get(cat_id)
            if cat:
                db.session.delete(cat)
                db.session.commit()
                flash('Category removed!', 'success')
        elif action == 'toggle':
            cat_id = request.form.get('category_id')
            cat = Category.query.get(cat_id)
            if cat:
                cat.is_active = not cat.is_active
                db.session.commit()
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/products', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_products():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price', 0))
            weight = float(request.form.get('weight', 1))
            category_id = request.form.get('category_id')
            is_new = 'is_new_collection' in request.form
            is_best = 'is_best_seller' in request.form
            # Check for cropped image data (base64)
            cropped_data = request.form.get('cropped_image_data')
            image_path = None
            if cropped_data and cropped_data.startswith('data:image'):
                # Save base64 image
                import base64, re
                match = re.match(r'data:image/(\w+);base64,(.*)', cropped_data, re.DOTALL)
                if match:
                    ext = match.group(1)
                    img_data = base64.b64decode(match.group(2))
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = f'{timestamp}cropped.{ext}'
                    path = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
                    os.makedirs(path, exist_ok=True)
                    with open(os.path.join(path, filename), 'wb') as f:
                        f.write(img_data)
                    image_path = f'uploads/products/{filename}'
            else:
                image_file = request.files.get('image')
                image_path = save_file(image_file, 'products') if image_file else None

            product = Product(name=name, description=description, price=price,
                              weight=weight, category_id=category_id, image=image_path,
                              is_new_collection=is_new, is_best_seller=is_best)
            db.session.add(product)
            db.session.commit()
            flash('Product added!', 'success')
        elif action == 'delete':
            pid = request.form.get('product_id')
            product = Product.query.get(pid)
            if product:
                db.session.delete(product)
                db.session.commit()
                flash('Product removed!', 'success')
        elif action == 'toggle_stock':
            pid = request.form.get('product_id')
            product = Product.query.get(pid)
            if product:
                product.is_stock_out = not product.is_stock_out
                db.session.commit()
    products = Product.query.all()
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/offers', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_offers():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            height_size = request.form.get('height_size', 'medium')
            sort_order = int(request.form.get('sort_order', 0))
            image_file = request.files.get('image')
            image_path = save_file(image_file, 'offers') if image_file else None
            offer = Offer(title=title, subtitle=subtitle, image=image_path,
                         height_size=height_size, sort_order=sort_order)
            db.session.add(offer)
            db.session.commit()
            # Check if more than 3
            active_count = Offer.query.filter_by(is_active=True).count()
            if active_count > 3:
                flash(f'Offer added! Note: You now have {active_count} active offers. Offers beyond the first 3 will appear in the "More Offers" section below.', 'success')
            else:
                flash('Offer added!', 'success')
        elif action == 'delete':
            oid = request.form.get('offer_id')
            offer = Offer.query.get(oid)
            if offer:
                db.session.delete(offer)
                db.session.commit()
                flash('Offer removed!', 'success')
        elif action == 'toggle':
            oid = request.form.get('offer_id')
            offer = Offer.query.get(oid)
            if offer:
                offer.is_active = not offer.is_active
                db.session.commit()
        elif action == 'update_size':
            oid = request.form.get('offer_id')
            new_size = request.form.get('height_size')
            offer = Offer.query.get(oid)
            if offer and new_size in OFFER_HEIGHT_MAP:
                offer.height_size = new_size
                db.session.commit()
                flash('Offer size updated!', 'success')
    offers = Offer.query.order_by(Offer.sort_order, Offer.created_at).all()
    return render_template('admin/offers.html', offers=offers, height_map=OFFER_HEIGHT_MAP)

@app.route('/admin/customers')
@login_required
@admin_required
def admin_customers():
    customers = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/customers.html', customers=customers)

# ─────────────────────────────────────────
# INIT DB & SEED
# ─────────────────────────────────────────

def seed_data():
    if User.query.filter_by(is_admin=True).first():
        return
    admin = User(name='Admin', email='admin@sripavani.com', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)

    cats = [
        Category(name='Necklaces', description='Elegant gold necklaces', image=None),
        Category(name='Bangles', description='Traditional gold bangles', image=None),
        Category(name='Earrings', description='Beautiful gold earrings', image=None),
        Category(name='Rings', description='Stunning gold rings', image=None),
        Category(name='Chains', description='Classic gold chains', image=None),
        Category(name='Pendants', description='Gorgeous gold pendants', image=None),
    ]
    for c in cats:
        db.session.add(c)
    db.session.commit()

    sample_products = [
        Product(name='Classic Gold Necklace', description='Elegant 1g gold necklace with intricate design', price=5999, weight=1, category_id=1, is_best_seller=True),
        Product(name='Temple Bangle Set', description='Traditional temple design gold bangles', price=7499, weight=1, category_id=2, is_new_collection=True),
        Product(name='Jhumka Earrings', description='Classic jhumka style gold earrings', price=4299, weight=1, category_id=3, is_best_seller=True),
        Product(name='Diamond Cut Ring', description='Beautiful diamond-cut gold ring', price=3999, weight=1, category_id=4, is_new_collection=True),
        Product(name='Rope Chain', description='Elegant rope-style gold chain', price=5499, weight=1, category_id=5, is_best_seller=True),
        Product(name='Lakshmi Pendant', description='Auspicious Lakshmi gold pendant', price=2999, weight=1, category_id=6, is_new_collection=True),
        Product(name='Choker Necklace', description='Stunning gold choker necklace', price=8999, weight=1, category_id=1),
        Product(name='Kada Bangle', description='Bold gold kada bangle', price=6799, weight=1, category_id=2),
    ]
    for p in sample_products:
        db.session.add(p)

    offer = Offer(title='Grand Diwali Sale', subtitle='Up to 30% off on all jewellery', image=None, is_active=True, height_size='medium')
    db.session.add(offer)
    db.session.commit()

with app.app_context():
    db.create_all()
    # Add height_size column if missing (for existing DBs)
    try:
        db.session.execute(db.text("ALTER TABLE offer ADD COLUMN height_size VARCHAR(20) DEFAULT 'medium'"))
        db.session.commit()
    except:
        pass
    try:
        db.session.execute(db.text("ALTER TABLE offer ADD COLUMN sort_order INTEGER DEFAULT 0"))
        db.session.commit()
    except:
        pass
    seed_data()

if __name__ == '__main__':
    app.run(debug=True)