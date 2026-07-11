import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import random

import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'singkong_keju_secret_key_123')

# Konfigurasi Database TiDB
tidb_host = os.getenv('TIDB_HOST')
tidb_port = os.getenv('TIDB_PORT')
tidb_user = os.getenv('TIDB_USER')
tidb_password = os.getenv('TIDB_PASSWORD')
tidb_db = os.getenv('TIDB_DATABASE')

if tidb_host and tidb_user:
    # URL Format untuk TiDB Serverless (menggunakan ssl_verify_cert dan ssl_verify_identity)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{tidb_user}:{tidb_password}@{tidb_host}:{tidb_port}/{tidb_db}?ssl_verify_cert=true&ssl_verify_identity=true"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 280
}
db = SQLAlchemy(app)

# Custom Jinja filter for Rupiah
@app.template_filter('rupiah')
def rupiah_format(value):
    return f"Rp {value:,.0f}".replace(',', '.')

# Model Database
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    reviews = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), nullable=False)
    group = db.Column(db.String(50), nullable=False) # 'unggulan', 'makanan_berat', 'makanan_ringan', 'minuman'
    stock = db.Column(db.Integer, default=100)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=True)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'), nullable=True)
    table_number = db.Column(db.String(20), nullable=False)
    table_category = db.Column(db.String(50), nullable=False) # VIP, Regular
    date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False) # Completed, Processed, Canceled, Pending
    product_summary = db.Column(db.String(255), nullable=False)
    
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    admin = db.relationship('Admin')
    
    payment = db.relationship('PaymentMethod', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Integer, nullable=False)
    
    menu = db.relationship('Menu')

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin') # 'admin' or 'kasir'

# Konfigurasi Cloudinary
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET'),
    secure = True
)

# Data awal menu telah dipindahkan ke database.sql dan diinisialisasi melalui TiDB / SQLite.

@app.route('/')
def index():
    unggulan = Menu.query.filter_by(group='unggulan').all()
    makanan_berat = Menu.query.filter_by(group='makanan_berat').all()
    makanan_ringan = Menu.query.filter_by(group='makanan_ringan').all()
    minuman = Menu.query.filter_by(group='minuman').all()
        
    return render_template(
        'index.html',
        unggulan=unggulan,
        makanan_berat=makanan_berat,
        makanan_ringan=makanan_ringan,
        minuman=minuman,
        midtrans_client_key=os.getenv('MIDTRANS_CLIENT_KEY', ''),
        midtrans_is_production=os.getenv('MIDTRANS_IS_PRODUCTION', 'False').lower() == 'true'
    )

with app.app_context():
    try:
        db.create_all()
        
        # Insert payment methods jika belum ada
        if not PaymentMethod.query.first():
            methods = ['Tunai', 'QRIS', 'Transfer']
            for m in methods:
                # pyrefly: ignore [unexpected-keyword]
                db.session.add(PaymentMethod(name=m))
            db.session.commit()
            
        # Insert default admin jika belum ada
        if not Admin.query.filter_by(username='admin').first():
            # pyrefly: ignore [unexpected-keyword]
            default_admin = Admin(username='admin', password='admin123', role='admin')
            db.session.add(default_admin)
            
        if not Admin.query.filter_by(username='kasir').first():
            # pyrefly: ignore [unexpected-keyword]
            default_kasir = Admin(username='kasir', password='kasir123', role='kasir')
            db.session.add(default_kasir)

        db.session.commit()
    except Exception as e:
        print(f"Gagal inisialisasi database: {str(e)}")

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    if session.get('role') != 'admin':
        return redirect(url_for('admin_kasir'))

    selected_date = request.args.get('date')
    if selected_date:
        try:
            today = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            today = datetime.now().date()
    else:
        today = datetime.now().date()
    # Total sales today
    today_orders = Order.query.filter(db.func.date(Order.date) == today).all()
    total_sales_today = sum([o.total_amount for o in today_orders if o.status == 'Completed'])
    
    total_orders = Order.query.count()
    low_stock = Menu.query.filter(Menu.stock < 10).count()
    popular_products = Menu.query.order_by(Menu.reviews.desc()).limit(2).all()
    recent_orders = Order.query.order_by(Order.id.desc()).limit(3).all()
    
    # Calculate sales for the last 7 days
    daily_sales = []
    max_sales = 0
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_orders = Order.query.filter(db.func.date(Order.date) == d).all()
        sales = sum([o.total_amount for o in day_orders if o.status == 'Completed'])
        daily_sales.append({
            'day': d.strftime('%a'),
            'sales': sales
        })
        if sales > max_sales:
            max_sales = sales
            
    # Calculate percentage heights for the bar chart
    for d in daily_sales:
        d['height'] = (d['sales'] / max_sales * 100) if max_sales > 0 else 0
        if d['height'] < 5:
            d['height'] = 5 # Minimum height for visibility
    
    return render_template('admin.html', 
                           total_sales_today=total_sales_today, 
                           total_orders=total_orders,
                           low_stock=low_stock,
                           popular_products=popular_products,
                           recent_orders=recent_orders,
                           daily_sales=daily_sales,
                           selected_date=selected_date)
@app.route('/admin/kasir')
def admin_kasir():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    if session.get('role') != 'kasir':
        return redirect(url_for('admin_dashboard'))

    menus = Menu.query.order_by(Menu.id.asc()).all()
    midtrans_is_prod = os.getenv('MIDTRANS_IS_PRODUCTION', 'False').lower() == 'true'
    return render_template('admin_kasir.html', menus=menus, active_page='kasir', midtrans_client_key=os.getenv('MIDTRANS_CLIENT_KEY', ''), midtrans_is_production=midtrans_is_prod)

@app.route('/admin/pending')
def admin_pending():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    if session.get('role') != 'kasir':
        return redirect(url_for('admin_dashboard'))

    pending_orders = Order.query.options(joinedload(Order.admin), joinedload(Order.payment)).filter_by(status='Pending').order_by(Order.date.asc()).all()
    return render_template('admin_pending.html', pending_orders=pending_orders, active_page='pending')

@app.route('/api/pending_updates')
def api_pending_updates():
    if not session.get('username') or session.get('role') != 'kasir':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Just return count and latest order ID for lightweight polling
    pending_orders = Order.query.filter_by(status='Pending').order_by(Order.date.desc()).all()
    
    # Also sum total pending amount to detect if amounts change
    total_amount = sum(o.total_amount for o in pending_orders)
    
    return jsonify({
        'count': len(pending_orders),
        'last_order_id': pending_orders[0].order_id if pending_orders else None,
        'total_amount': total_amount
    })

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    try:
        data = request.json
        table_number = data.get('table_number')
        if not table_number or str(table_number).strip() == '':
            table_number = 'Takeaway'
        items = data.get('items', [])

        if not items:
            return jsonify({"success": False, "message": "Keranjang kosong"}), 400

        # Cast all item IDs to integers to prevent dictionary lookup failures (string vs int keys)
        for item in items:
            try:
                item['id'] = int(item['id'])
            except (ValueError, TypeError):
                return jsonify({"success": False, "message": "Format ID Menu tidak valid"}), 400

        total_amount = 0
        product_summary_parts = []
        
        # Batch fetch semua menu
        menu_ids = [item['id'] for item in items]
        menus_db = {m.id: m for m in Menu.query.filter(Menu.id.in_(menu_ids)).all()}

        # Validasi stok & kalkulasi total
        for item in items:
            menu = menus_db.get(item['id'])
            if not menu:
                return jsonify({"success": False, "message": f"Menu ID {item['id']} tidak ditemukan"}), 404
            
            qty = item['qty']
            if menu.stock < qty:
                return jsonify({"success": False, "message": f"Stok {menu.name} tidak mencukupi"}), 400
            
            total_amount += (menu.price * qty)
            product_summary_parts.append(f"{qty}x {menu.name}")
        
        # Tambahkan pajak 10%
        tax = round(total_amount * 0.1)
        grand_total = total_amount + tax

        status_val = data.get('status')
        pm_name = data.get('payment_method', 'tunai')
        
        # Jika dari Kasir (tanpa status), tunai = Completed, digital = Pending
        if not status_val:
            if pm_name.lower() in ['qris', 'transfer']:
                status_val = 'Pending'
            else:
                status_val = 'Completed'
            
        pm = PaymentMethod.query.filter(db.func.lower(PaymentMethod.name) == pm_name.lower()).first()

        order_id = data.get('order_id')
        if order_id:
            # Selesaikan pesanan lama (stok sudah dipotong saat customer buat order)
            order = Order.query.filter_by(order_id=order_id).first()
            if order:
                if pm:
                    order.payment_method_id = pm.id
                    
                # Catat siapa yang memproses transaksi ini
                if session.get('role') in ['admin', 'kasir'] and session.get('admin_id'):
                    order.admin_id = session.get('admin_id')
                    
                if pm_name.lower() in ['qris', 'transfer']:
                    order.status = 'Pending'
                else:
                    order.status = 'Completed'
                    # Increment sales (reviews acts as sales count for popular products)
                    for item in items:
                        menu = menus_db.get(item['id'])
                        if menu:
                            menu.reviews += item['qty']
                db.session.commit()
                
                # Jika metode digital, tidak return di sini, kita generate snap_token di bawah
                if pm_name.lower() not in ['qris', 'transfer']:
                    return jsonify({"success": True, "message": "Pesanan berhasil diselesaikan", "order_id": order_id})
        else:
            for item in items:
                menu = menus_db.get(item['id'])
                if menu:
                    menu.stock -= item['qty']
                    if status_val == 'Completed':
                        menu.reviews += item['qty']
                
            # Buat Order Baru
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            new_order = Order(
                # pyrefly: ignore [unexpected-keyword]
                order_id=order_id,
                # pyrefly: ignore [unexpected-keyword]
                customer_name=data.get('customer_name'),
                # pyrefly: ignore [unexpected-keyword]
                payment_method_id=pm.id if pm else None,
                # pyrefly: ignore [unexpected-keyword]
                table_number=table_number,
                # pyrefly: ignore [unexpected-keyword]
                table_category="Regular",
                # pyrefly: ignore [unexpected-keyword]
                date=datetime.now(),
                # pyrefly: ignore [unexpected-keyword]
                total_amount=grand_total,
                # pyrefly: ignore [unexpected-keyword]
                status=status_val,
                # pyrefly: ignore [unexpected-keyword]
                product_summary=", ".join(product_summary_parts),
                # pyrefly: ignore [unexpected-keyword]
                admin_id=session.get('admin_id') if session.get('role') in ['admin', 'kasir'] else None
            )
            
            for item in items:
                menu = menus_db.get(item['id'])
                if menu:
                    order_item = OrderItem(
                        # pyrefly: ignore [unexpected-keyword]
                        menu_id=menu.id,
                        # pyrefly: ignore [unexpected-keyword]
                        quantity=item['qty'],
                        # pyrefly: ignore [unexpected-keyword]
                        price_per_unit=menu.price
                    )
                    new_order.items.append(order_item)
            
            db.session.add(new_order)
            db.session.commit()
        
        # --- BLOK INI AKAN DIJALANKAN OLEH PESANAN BARU MAUPUN LAMA JIKA MEMILIH QRIS ---
        snap_token = None
        if data.get('payment_method') in ['qris', 'transfer']:
            try:
                # pyrefly: ignore [missing-import]
                import midtransclient
                snap = midtransclient.Snap(
                    is_production=os.getenv('MIDTRANS_IS_PRODUCTION', 'False').lower() == 'true',
                    server_key=os.getenv('MIDTRANS_SERVER_KEY', ''),
                    client_key=os.getenv('MIDTRANS_CLIENT_KEY', '')
                )
                param = {
                    "transaction_details": {
                        "order_id": order_id,
                        "gross_amount": grand_total
                    },
                    "customer_details": {
                        "first_name": data.get('customer_name', 'Customer') or 'Customer',
                        "email": "customer@singkongkeju.com"
                    }
                }
                transaction = snap.create_transaction(param)
                snap_token = transaction['token']
            except Exception as e:
                print(f"Midtrans Error: {e}")
        
        return jsonify({
            "success": True, 
            "message": "Pesanan berhasil diproses",
            "order_id": order_id,
            "snap_token": snap_token
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/midtrans/webhook', methods=['POST'])
def midtrans_webhook():
    try:
        data = request.json
        order_id = data.get('order_id')
        transaction_status = data.get('transaction_status')
        
        order = Order.query.filter_by(order_id=order_id).first()
        if order:
            if transaction_status in ['capture', 'settlement'] and order.status != 'Completed':
                order.status = 'Completed'
                for item in order.items:
                    if item.menu:
                        item.menu.reviews += item.quantity
            elif transaction_status in ['cancel', 'deny', 'expire'] and order.status != 'Canceled':
                order.status = 'Canceled'
                for item in order.items:
                    if item.menu:
                        item.menu.stock += item.quantity
            elif transaction_status == 'pending':
                order.status = 'Pending'
            db.session.commit()
            
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/success_order', methods=['POST'])
def success_order():
    try:
        data = request.json
        order_id = data.get('order_id')
        
        order = Order.query.filter_by(order_id=order_id).first()
        if order and order.status != 'Completed':
            order.status = 'Completed'
            # Increment sales
            for item in order.items:
                if item.menu:
                    item.menu.reviews += item.quantity
            db.session.commit()
            return jsonify({"success": True})
        return jsonify({"success": False})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/cancel_order', methods=['POST'])
def cancel_order():
    try:
        data = request.json
        order_id = data.get('order_id')
        items = data.get('items', [])
        
        order = Order.query.filter_by(order_id=order_id).first()
        if order and order.status == 'Pending':
            order.status = 'Canceled'
            # Kembalikan stok
            for item in items:
                menu = Menu.query.get(item['id'])
                if menu:
                    menu.stock += item['qty']
            db.session.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Order tidak valid"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/order/status/<order_id>', methods=['GET'])
def get_order_status(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({"success": False, "message": "Pesanan tidak ditemukan"}), 404
    return jsonify({"success": True, "status": order.status})

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    if not session.get('role'):
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({"success": False, "message": "Pesanan tidak ditemukan"}), 404
        
    # Parse product_summary (e.g. "2x Singkong Keju Original, 1x Es Teh")
    items = []
    for part in order.product_summary.split(','):
        part = part.strip()
        if 'x ' in part:
            qty_str, name = part.split('x ', 1)
            menu = Menu.query.filter_by(name=name).first()
            if menu:
                items.append({
                    "id": menu.id,
                    "name": menu.name,
                    "price": menu.price,
                    "category": menu.category,
                    "qty": int(qty_str),
                    "stock": menu.stock
                })
    
    return jsonify({
        "success": True,
        "order": {
            "order_id": order.order_id,
            "table_number": order.table_number,
            "total_amount": order.total_amount,
            "items": items
        }
    })

@app.route('/api/orders/<order_id>/complete', methods=['POST'])
def complete_order(order_id):
    if session.get('role') != 'kasir' and session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
        
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify({"success": False, "message": "Pesanan tidak ditemukan"}), 404
            
        order.status = 'Completed'
        db.session.commit()
        return jsonify({"success": True, "message": "Pesanan berhasil diselesaikan"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/admin/menu')
def admin_menu():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    if session.get('role') != 'admin':
        return redirect(url_for('admin_kasir'))

    menus = Menu.query.order_by(Menu.id.desc()).all()
    return render_template('admin_menu.html', menus=menus)

@app.route('/api/menu/add', methods=['POST'])
def add_menu():
    if session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    try:
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description', '')
        price = request.form.get('price')
        stock = request.form.get('stock', 100)
        group = request.form.get('group', 'unggulan')
        
        image_url = 'https://placehold.co/300x250/fdfbf7/7a6353?text=New+Menu' # Default
        image_file = request.files.get('image')
        
        if image_file and image_file.filename != '':
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get("secure_url")
            
        new_menu = Menu(
            # pyrefly: ignore [unexpected-keyword]
            name=name,
            # pyrefly: ignore [unexpected-keyword]
            category=category,
            # pyrefly: ignore [unexpected-keyword]
            description=description,
            # pyrefly: ignore [unexpected-keyword]
            price=int(price),
            # pyrefly: ignore [unexpected-keyword]
            stock=int(stock),
            # pyrefly: ignore [unexpected-keyword]
            group=group,
            # pyrefly: ignore [unexpected-keyword]
            image=image_url
        )
        db.session.add(new_menu)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Menu berhasil ditambahkan!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/menu/update/<int:menu_id>', methods=['POST'])
def update_menu(menu_id):
    if session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
        
    try:
        menu = Menu.query.get(menu_id)
        if not menu:
            return jsonify({"success": False, "message": "Menu tidak ditemukan"}), 404
            
        menu.name = request.form.get('name', menu.name)
        menu.category = request.form.get('category', menu.category)
        menu.description = request.form.get('description', menu.description)
        menu.price = int(request.form.get('price', menu.price))
        menu.stock = int(request.form.get('stock', menu.stock))
        menu.group = request.form.get('group', menu.group)
        
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            upload_result = cloudinary.uploader.upload(image_file)
            menu.image = upload_result.get("secure_url")
            
        db.session.commit()
        return jsonify({"success": True, "message": "Menu berhasil diperbarui!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/menu/delete/<int:menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    if session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
        
    try:
        menu = Menu.query.get(menu_id)
        if not menu:
            return jsonify({"success": False, "message": "Menu tidak ditemukan"}), 404
            
        db.session.delete(menu)
        db.session.commit()
        return jsonify({"success": True, "message": "Menu berhasil dihapus!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500



@app.route('/admin/stock')
def admin_stock():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    if session.get('role') != 'admin':
        return redirect(url_for('admin_kasir'))

    total_menu = Menu.query.count()
    low_stock = Menu.query.filter(Menu.stock < 10).count()
    menus = Menu.query.order_by(Menu.id.asc()).all()
    
    # Calculate last updated string
    latest_menu = Menu.query.order_by(Menu.updated_at.desc()).first()
    last_updated_str = "Belum Ada Update"
    if latest_menu and latest_menu.updated_at:
        diff = datetime.now() - latest_menu.updated_at
        if diff.days > 0:
            last_updated_str = f"{diff.days} Hari Lalu"
        elif diff.seconds >= 3600:
            last_updated_str = f"{diff.seconds // 3600} Jam Lalu"
        elif diff.seconds >= 60:
            last_updated_str = f"{diff.seconds // 60} Menit Lalu"
        else:
            last_updated_str = "Baru Saja"
    
    return render_template('admin_stock.html',
                           total_menu=total_menu,
                           low_stock=low_stock,
                           menus=menus,
                           last_updated_str=last_updated_str)

@app.route('/api/stock/update/<int:menu_id>', methods=['POST'])
def update_stock(menu_id):
    try:
        data = request.json
        new_stock = data.get('stock')
        
        if new_stock is None:
            return jsonify({"success": False, "message": "Stock value is required"}), 400
            
        menu = Menu.query.get(menu_id)
        if not menu:
            return jsonify({"success": False, "message": "Menu not found"}), 404
            
        menu.stock = int(new_stock)
        menu.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({"success": True, "message": "Stock updated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/admin/orders')
def admin_orders():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    if session.get('role') not in ['admin', 'kasir']:
        return redirect(url_for('login_page'))

    selected_date = request.args.get('date')
    selected_status = request.args.get('status')
    selected_range = request.args.get('range')
    selected_month = request.args.get('month')
    
    query = Order.query.options(joinedload(Order.admin), joinedload(Order.payment))
    if selected_date:
        query = query.filter(db.func.date(Order.date) == selected_date)
    if selected_month:
        query = query.filter(db.func.strftime('%Y-%m', Order.date) == selected_month)
    if selected_range:
        try:
            from datetime import datetime, timedelta
            days = int(selected_range)
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(Order.date >= start_date)
        except ValueError:
            pass
            
    if selected_status:
        query = query.filter(Order.status == selected_status)
        
    orders = query.order_by(Order.id.desc()).all()
    total_volume = sum([o.total_amount for o in orders if o.status == 'Completed'])
    total_orders = len(orders)
    
    completed = len([o for o in orders if o.status == 'Completed'])
    pending = len([o for o in orders if o.status == 'Pending'])
    
    completed_pct = round((completed / total_orders * 100) if total_orders > 0 else 0)
    pending_pct = round((pending / total_orders * 100) if total_orders > 0 else 0)
    
    return render_template('admin_orders.html',
                           orders=orders,
                           total_volume=total_volume,
                           completed=completed,
                           pending=pending,
                           completed_pct=completed_pct,
                           pending_pct=pending_pct,
                           selected_date=selected_date or '',
                           selected_month=selected_month or '',
                           selected_range=selected_range or '',
                           selected_status=selected_status or '')

@app.route('/admin/receipt/<order_id>')
def print_receipt(order_id):
    if not session.get('username') or session.get('role') not in ['admin', 'kasir']:
        return redirect(url_for('login_page'))
    
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return "Order not found", 404
        
    return render_template('receipt.html', order=order)

@app.route('/admin/orders/export/csv')
def export_orders_csv():
    if not session.get('username') or session.get('role') not in ['admin', 'kasir']:
        return redirect(url_for('login_page'))
        
    selected_date = request.args.get('date')
    selected_status = request.args.get('status')
    selected_range = request.args.get('range')
    selected_month = request.args.get('month')
    
    query = Order.query
    if selected_date:
        query = query.filter(db.func.date(Order.date) == selected_date)
    if selected_month:
        query = query.filter(db.func.strftime('%Y-%m', Order.date) == selected_month)
    if selected_range:
        try:
            from datetime import datetime, timedelta
            days = int(selected_range)
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(Order.date >= start_date)
        except ValueError:
            pass
            
    if selected_status:
        query = query.filter(Order.status == selected_status)
        
    orders = query.order_by(Order.date.desc()).all()
    
    import io
    import csv
    from flask import Response
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Order ID', 'Table Number', 'Table Category', 'Date', 'Product Summary', 'Total Amount', 'Status'])
    
    for order in orders:
        writer.writerow([
            order.order_id,
            order.table_number,
            order.table_category,
            order.date.strftime('%Y-%m-%d %H:%M:%S'),
            order.product_summary,
            order.total_amount,
            order.status
        ])
        
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=order_history.csv'
    return response

@app.route('/admin/report')
def admin_report():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    if session.get('role') != 'admin':
        return redirect(url_for('admin_kasir'))

    selected_date = request.args.get('date')
    selected_month = request.args.get('month')
    selected_range = request.args.get('range')
    
    query_orders = Order.query.filter(Order.status == 'Completed')
    total_revenue_query = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status == 'Completed')
    
    if selected_date:
        query_orders = query_orders.filter(db.func.date(Order.date) == selected_date)
        total_revenue_query = total_revenue_query.filter(db.func.date(Order.date) == selected_date)
    if selected_month:
        query_orders = query_orders.filter(db.func.strftime('%Y-%m', Order.date) == selected_month)
        total_revenue_query = total_revenue_query.filter(db.func.strftime('%Y-%m', Order.date) == selected_month)
    if selected_range:
        try:
            days = int(selected_range)
            start_date = datetime.now() - timedelta(days=days)
            query_orders = query_orders.filter(Order.date >= start_date)
            total_revenue_query = total_revenue_query.filter(Order.date >= start_date)
        except ValueError:
            pass
            
    total_revenue = total_revenue_query.scalar() or 0
    
    orders_count = query_orders.count()
    best_seller = Menu.query.order_by(Menu.reviews.desc()).first()
    
    # Calculate Product Performance using OrderItem
    from collections import defaultdict
    category_sales = defaultdict(int)
    total_items_sold = 0
    
    # Query all completed orders in the filtered range
    order_ids = [o.id for o in query_orders.all()]
    
    if order_ids:
        # Get all items for these orders joined with Menu to get group
        items = db.session.query(OrderItem, Menu.group).join(Menu).filter(OrderItem.order_id.in_(order_ids)).all()
        for item, menu_group in items:
            group_name = menu_group.replace('_', ' ').title()
            category_sales[group_name] += item.quantity
            total_items_sold += item.quantity
                    
    # Sort categories by sales
    sorted_cats = sorted(category_sales.items(), key=lambda x: x[1], reverse=True)
    top_categories = []
    for cat, qty in sorted_cats[:3]:
        pct = round((qty / total_items_sold * 100) if total_items_sold > 0 else 0)
        top_categories.append({'name': cat, 'pct': pct})
        
    recommended_focus = top_categories[0]['name'] if top_categories else 'Tidak ada'
    
    # Get top tables performance
    tables_query = db.session.query(
        Order.table_number,
        Order.table_category,
        db.func.count(Order.id).label('total_orders'),
        db.func.sum(Order.total_amount).label('lifetime_value'),
        db.func.max(Order.date).label('last_activity')
    ).filter(Order.status == 'Completed')
    if selected_date:
        tables_query = tables_query.filter(db.func.date(Order.date) == selected_date)
    if selected_month:
        tables_query = tables_query.filter(db.func.strftime('%Y-%m', Order.date) == selected_month)
        
    tables = tables_query.group_by(Order.table_number, Order.table_category).order_by(db.text('total_orders DESC')).limit(4).all()
    
    import json
    import calendar
    
    end_date_trend = datetime.now()
    days_to_show = 7
    
    if selected_range:
        try:
            days_to_show = int(selected_range)
        except ValueError:
            pass
    elif selected_date:
        try:
            end_date_trend = datetime.strptime(selected_date, '%Y-%m-%d')
            end_date_trend = end_date_trend.replace(hour=23, minute=59, second=59)
        except ValueError:
            pass
    elif selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            _, last_day = calendar.monthrange(year, month)
            end_date_trend = datetime(year, month, last_day, 23, 59, 59)
            days_to_show = last_day
        except ValueError:
            pass
            
    start_date_trend = end_date_trend - timedelta(days=days_to_show - 1)
    start_date_trend = start_date_trend.replace(hour=0, minute=0, second=0, microsecond=0)
    
    daily_revenue_query = db.session.query(
        db.func.date(Order.date).label('day'),
        db.func.sum(Order.total_amount).label('revenue')
    ).filter(
        Order.status == 'Completed',
        Order.date >= start_date_trend,
        Order.date <= end_date_trend
    ).group_by(db.func.date(Order.date)).all()
    
    revenue_data_dict = {str(row.day): int(row.revenue) for row in daily_revenue_query if row.day}
    
    revenue_labels = []
    revenue_values = []
    for i in range(days_to_show):
        d = (start_date_trend + timedelta(days=i)).date()
        label = d.strftime('%d %b')
        revenue_labels.append(label)
        revenue_values.append(revenue_data_dict.get(str(d), 0))
        
    revenue_chart_data = json.dumps({
        'labels': revenue_labels,
        'values': revenue_values
    })
    
    return render_template('admin_report.html',
                           total_revenue=total_revenue,
                           orders_count=orders_count,
                           best_seller=best_seller,
                           top_categories=top_categories,
                           recommended_focus=recommended_focus,
                           top_tables=tables,
                           revenue_chart_data=revenue_chart_data,
                           selected_date=selected_date or '',
                           selected_month=selected_month or '')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.password == password:
        session['username'] = admin.username
        session['role'] = admin.role
        session['admin_id'] = admin.id
        return jsonify({"success": True, "message": "Login successful!"})
    else:
        return jsonify({"success": False, "message": "Username atau password salah."}), 401

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image file provided."}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file."}), 400
        
    try:
        # Upload the file to Cloudinary
        upload_result = cloudinary.uploader.upload(file)
        # Return the secure URL
        return jsonify({
            "success": True, 
            "message": "Upload successful", 
            "url": upload_result.get("secure_url")
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/test_db', methods=['GET'])
def test_db():
    try:
        # Menggunakan text() dari sqlalchemy untuk mengeksekusi query raw
        result = db.session.execute(text("SELECT VERSION()"))
        version = result.scalar()
        return jsonify({"success": True, "message": "Berhasil terhubung ke database!", "version": version})
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal terhubung: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
