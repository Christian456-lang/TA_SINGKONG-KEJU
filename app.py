import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
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

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(20), unique=True, nullable=False)
    table_number = db.Column(db.String(10), nullable=False)
    table_category = db.Column(db.String(20), nullable=False) # VIP, Regular
    date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False) # Completed, Processed, Canceled, Pending
    product_summary = db.Column(db.String(255), nullable=False)

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

# ── Menu Unggulan ──────────────────────────────────────────────
UNGGULAN = [
    {
        "id": 101,
        "name": "Singkong Keju D9",
        "category": "OLAHAN SINGKONG",
        "price": 25000,
        "rating": 5.0,
        "reviews": 1244,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Singkong+Keju"
    },
    {
        "id": 102,
        "name": "Getuk D9 Pelangi",
        "category": "MANIS TRADISIONAL",
        "price": 20000,
        "rating": 4.9,
        "reviews": 982,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Getuk+Pelangi"
    },
    {
        "id": 103,
        "name": "Kroket Singkong D9",
        "category": "CEMILAN GURIH",
        "price": 22000,
        "rating": 4.8,
        "reviews": 843,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Kroket+Singkong"
    },
    {
        "id": 104,
        "name": "Prol Tape Keju D9",
        "category": "VARIAN TAPE",
        "price": 35000,
        "rating": 4.9,
        "reviews": 528,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Prol+Tape"
    },
    {
        "id": 105,
        "name": "Timus Manis D9",
        "category": "KUDAPAN SORE",
        "price": 18000,
        "rating": 4.7,
        "reviews": 315,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Timus+Manis"
    },
    {
        "id": 106,
        "name": "Gemblong Cotot D9",
        "category": "TRADISI SALATIGA",
        "price": 20000,
        "rating": 4.8,
        "reviews": 526,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Gemblong+Cotot"
    }
]

# ── Makanan Berat ──────────────────────────────────────────────
MAKANAN_BERAT = [
    {
        "id": 1,
        "name": "Bakmi Jawa Godog (Rebus)",
        "category": "MAKANAN BERAT",
        "description": "Mie rebus tradisional dengan kuah kaldu kentol dan rempah pilihan.",
        "price": 22000,
        "rating": 4.5,
        "reviews": 320,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Bakmi+Godog"
    },
    {
        "id": 2,
        "name": "Bakmi Jawa Goreng",
        "category": "MAKANAN BERAT",
        "description": "Mie goreng khas Jawa dengan aroma smokey dan cita rasa manis gurih.",
        "price": 22000,
        "rating": 4.5,
        "reviews": 285,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Bakmi+Goreng"
    },
    {
        "id": 3,
        "name": "Nasi Goreng Spesial",
        "category": "FAVORIT",
        "description": "Nasi goreng dengan telur, ayam, dan sayuran segar khas D9.",
        "price": 25000,
        "rating": 4.8,
        "reviews": 510,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Nasgor+Spesial"
    },
    {
        "id": 4,
        "name": "Nasi Goreng Babat",
        "category": "MAKANAN BERAT",
        "description": "Nasi goreng gurih dengan potongan babat empuk bumbu rempah.",
        "price": 28000,
        "rating": 4.6,
        "reviews": 198,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Nasgor+Babat"
    },
    {
        "id": 5,
        "name": "Nasi Pecel",
        "category": "MENU TRADISIONAL",
        "description": "Sayuran segar dengan siraman bumbu kacang gurih dan rempeyek renyah.",
        "price": 18000,
        "rating": 4.7,
        "reviews": 425,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Nasi+Pecel"
    },
    {
        "id": 6,
        "name": "Nasi Ayam Goreng",
        "category": "MAKANAN BERAT",
        "description": "Ayam goreng bumbu lengkap dengan sambal kentol dan lalapan.",
        "price": 25000,
        "rating": 4.8,
        "reviews": 480,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Nasi+Ayam+Goreng"
    },
    {
        "id": 7,
        "name": "Nasi Ayam Bakar",
        "category": "MAKANAN BERAT",
        "description": "Ayam bakar bumbu kecap meresap dengan aroma bakaran yang menggoda.",
        "price": 26000,
        "rating": 4.9,
        "reviews": 390,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Nasi+Ayam+Bakar"
    },
    {
        "id": 8,
        "name": "Soto Ayam / Sop",
        "category": "MENU SEGAR",
        "description": "Soto ayam kuah bening segar dengan irisan dan rempah dan kuva gurih.",
        "price": 20000,
        "rating": 4.6,
        "reviews": 310,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Soto+Ayam"
    },
]

# ── Makanan Ringan ─────────────────────────────────────────────
MAKANAN_RINGAN = [
    {
        "id": 9,
        "name": "Singkong Keju Original",
        "category": "OLAHAN TERLARIS",
        "description": "Singkong goreng renyah dengan taburan keju yang melimpah.",
        "price": 25000,
        "rating": 5.0,
        "reviews": 1244,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Singkong+Keju"
    },
    {
        "id": 10,
        "name": "Singkong Keju Cokelat / Meises",
        "category": "MANIS TRADISIONAL",
        "description": "Perpaduan gurihnya singkong dengan manisnya cokelat meises.",
        "price": 25000,
        "rating": 4.9,
        "reviews": 982,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Singkong+Cokelat"
    },
    {
        "id": 11,
        "name": "Singkong Sambal Roa",
        "category": "CAMILAN GURIH",
        "description": "Singkong goreng khas D9 disajikan dengan sambal roa pedas mantap.",
        "price": 22000,
        "rating": 4.8,
        "reviews": 843,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Singkong+Sambal"
    },
    {
        "id": 12,
        "name": "Tahu Serasi Goreng",
        "category": "KHAS BANDUNGAN",
        "description": "Tahu goreng khas Bandungan yang lembut dan gurih.",
        "price": 18000,
        "rating": 4.7,
        "reviews": 315,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Tahu+Serasi"
    },
    {
        "id": 13,
        "name": "Tempe Mendoan",
        "category": "GORENGAN FAVORIT",
        "description": "Tempe goreng tepung setengah matang dengan irisan daun bawang.",
        "price": 15000,
        "rating": 4.6,
        "reviews": 290,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Tempe+Mendoan"
    },
    {
        "id": 14,
        "name": "Pisang Goreng",
        "category": "MANIS ALAMI",
        "description": "Pisang goreng manis dengan pilihan topping keju atau cokelat.",
        "price": 18000,
        "rating": 4.7,
        "reviews": 350,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Pisang+Goreng"
    },
    {
        "id": 15,
        "name": "Kroket Singkong",
        "category": "CAMILAN GURIH",
        "description": "Kroket lembut berbahan dasar singkong pilihan.",
        "price": 20000,
        "rating": 4.8,
        "reviews": 526,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Kroket+Singkong"
    },
    {
        "id": 16,
        "name": "Tape Goreng",
        "category": "MANIS LEGIT",
        "description": "Tape singkong goreng yang manis dan legit.",
        "price": 15000,
        "rating": 4.5,
        "reviews": 210,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Tape+Goreng"
    },
    {
        "id": 17,
        "name": "Getuk Goreng",
        "category": "TRADISI SALATIGA",
        "description": "Getuk singkong manis yang digoreng hingga renyah di luar.",
        "price": 18000,
        "rating": 4.8,
        "reviews": 420,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Getuk+Goreng"
    },
    {
        "id": 18,
        "name": "Roti Bakar (Aneka Topping)",
        "category": "CAMILAN POPULER",
        "description": "Roti bakar hangat dengan berbagai pilihan topping toast.",
        "price": 20000,
        "rating": 4.6,
        "reviews": 380,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Roti+Bakar"
    },
]

# ── Minuman ────────────────────────────────────────────────────
MINUMAN = [
    {
        "id": 19,
        "name": "Teh Poci",
        "category": "SEDUHAN TRADISIONAL",
        "description": "Teh poci tradisional yang harum dan menyegarkan.",
        "price": 13000,
        "rating": 4.8,
        "reviews": 860,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Teh+Poci"
    },
    {
        "id": 20,
        "name": "Es Teh Kampul",
        "category": "SEGARNYA ALAMI",
        "description": "Es teh segar dengan sensasi kampul yang khas.",
        "price": 8000,
        "rating": 4.7,
        "reviews": 945,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Es+Teh+Kampul"
    },
    {
        "id": 21,
        "name": "Wedang Uwuh",
        "category": "SEDUHAN ALAMI",
        "description": "Wedang uwuh hangat dengan rempah-rempah tradisional.",
        "price": 12000,
        "rating": 4.9,
        "reviews": 990,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Wedang+Uwuh"
    },
    {
        "id": 22,
        "name": "Wedang Jahe",
        "category": "HANGAT MENYEHATKAN",
        "description": "Wedang jahe hangat yang menyehatkan tubuh.",
        "price": 10000,
        "rating": 4.7,
        "reviews": 710,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Wedang+Jahe"
    },
    {
        "id": 23,
        "name": "Wedang Ronde",
        "category": "LEGENDA HANGAT",
        "description": "Wedang ronde dengan isian kacang yang gurih.",
        "price": 15000,
        "rating": 4.8,
        "reviews": 850,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Wedang+Ronde"
    },
    {
        "id": 24,
        "name": "Kopi Hitam Tubruk",
        "category": "KOPI KLASIK",
        "description": "Kopi hitam tubruk khas yang kuat dan nikmat.",
        "price": 12000,
        "rating": 4.6,
        "reviews": 620,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Kopi+Tubruk"
    },
    {
        "id": 25,
        "name": "Kopi Susu",
        "category": "LEMBUT & CREAMY",
        "description": "Kopi susu lembut yang creamy dan nikmat.",
        "price": 18000,
        "rating": 4.9,
        "reviews": 1050,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Kopi+Susu"
    },
    {
        "id": 26,
        "name": "Es Campur",
        "category": "MINUMAN PALING SEGAR",
        "description": "Es campur segar dengan aneka buah dan sirup.",
        "price": 22000,
        "rating": 4.8,
        "reviews": 880,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Es+Campur"
    },
    {
        "id": 27,
        "name": "Es Teler",
        "category": "FAVORIT NUSANTARA",
        "description": "Es teler segar dengan alpukat, kelapa, dan nangka.",
        "price": 25000,
        "rating": 4.9,
        "reviews": 730,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Es+Teler"
    },
    {
        "id": 28,
        "name": "Aneka Jus Buah",
        "category": "FRESH & SEHAT",
        "description": "Jus buah segar pilihan yang menyehatkan.",
        "price": 15000,
        "rating": 4.7,
        "reviews": 480,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Jus+Buah"
    },
    {
        "id": 29,
        "name": "Lemon Tea (Panas / Es)",
        "category": "SEGAR & SEHAT",
        "description": "Lemon tea yang segar dan menyehatkan.",
        "price": 10000,
        "rating": 4.6,
        "reviews": 390,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Lemon+Tea"
    },
    {
        "id": 30,
        "name": "Teh Manis / Tawar",
        "category": "MINUMAN SEPANJANG",
        "description": "Teh manis atau tawar hangat/dingin.",
        "price": 5000,
        "rating": 4.5,
        "reviews": 1200,
        "image": "https://placehold.co/300x250/fdfbf7/7a6353?text=Teh+Manis"
    },
]

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
        
        # Insert default admin jika belum ada
        if not Admin.query.filter_by(username='admin').first():
            # pyrefly: ignore [unexpected-keyword]
            default_admin = Admin(username='admin', password='admin123', role='admin')
            db.session.add(default_admin)
            
        if not Admin.query.filter_by(username='kasir').first():
            # pyrefly: ignore [unexpected-keyword]
            default_kasir = Admin(username='kasir', password='kasir123', role='kasir')
            db.session.add(default_kasir)

        # Cek jika data menu kosong, maka isi dengan data awal
        if not Menu.query.first():
            def seed_data(data_list, group_name):
                for item in data_list:
                    menu = Menu(
                        # pyrefly: ignore [unexpected-keyword]
                        name=item.get('name'),
                        # pyrefly: ignore [unexpected-keyword]
                        category=item.get('category'),
                        # pyrefly: ignore [unexpected-keyword]
                        description=item.get('description', ''),
                        # pyrefly: ignore [unexpected-keyword]
                        price=item.get('price'),
                        # pyrefly: ignore [unexpected-keyword]
                        rating=item.get('rating', 0.0),
                        # pyrefly: ignore [unexpected-keyword]
                        reviews=item.get('reviews', 0),
                        # pyrefly: ignore [unexpected-keyword]
                        image=item.get('image', ''),
                        # pyrefly: ignore [unexpected-keyword]
                        group=group_name,
                        # pyrefly: ignore [unexpected-keyword]
                        stock=random.randint(0, 150)
                    )
                    db.session.add(menu)
                    
            seed_data(UNGGULAN, 'unggulan')
            seed_data(MAKANAN_BERAT, 'makanan_berat')
            seed_data(MAKANAN_RINGAN, 'makanan_ringan')
            seed_data(MINUMAN, 'minuman')

        db.session.commit()
    except Exception as e:
        print(f"Gagal inisialisasi database: {str(e)}")

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('username'):
        return redirect(url_for('login_page'))
    if session.get('role') != 'admin':
        return redirect(url_for('admin_kasir'))

    today = datetime.now().date()
    # Total sales today
    today_orders = Order.query.filter(db.func.date(Order.date) == today).all()
    total_sales_today = sum([o.total_amount for o in today_orders if o.status == 'Completed'])
    
    total_orders = Order.query.count()
    low_stock = Menu.query.filter(Menu.stock < 10).count()
    popular_products = Menu.query.order_by(Menu.reviews.desc()).limit(2).all()
    recent_orders = Order.query.order_by(Order.date.desc()).limit(3).all()
    
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
                           daily_sales=daily_sales)
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

    pending_orders = Order.query.filter_by(status='Pending').order_by(Order.date.asc()).all()
    return render_template('admin_pending.html', pending_orders=pending_orders, active_page='pending')

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    try:
        data = request.json
        table_number = data.get('table_number')
        items = data.get('items', [])

        if not items:
            return jsonify({"success": False, "message": "Keranjang kosong"}), 400

        total_amount = 0
        product_summary_parts = []

        # Validasi stok & kalkulasi total
        for item in items:
            menu = Menu.query.get(item['id'])
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

        status_val = data.get('status', 'Completed')
        if status_val == 'Pending' and data.get('payment_method') != 'tunai':
            status_val = 'Completed'
            
        order_id = data.get('order_id')
        if order_id:
            # Selesaikan pesanan lama (stok sudah dipotong saat customer buat order)
            order = Order.query.filter_by(order_id=order_id).first()
            if order:
                order.status = 'Completed'
                # Increment sales (reviews acts as sales count for popular products)
                for item in items:
                    menu = Menu.query.get(item['id'])
                    if menu:
                        menu.reviews += item['qty']
                db.session.commit()
                return jsonify({"success": True, "message": "Pesanan berhasil diselesaikan", "order_id": order_id})

        # Kurangi stok jika ini pesanan baru, dan tambah review jika langsung Completed
        for item in items:
            menu = Menu.query.get(item['id'])
            menu.stock -= item['qty']
            if status_val == 'Completed':
                menu.reviews += item['qty']
            
        # Buat Order Baru
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        new_order = Order(
            # pyrefly: ignore [unexpected-keyword]
            order_id=order_id,
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
            product_summary=", ".join(product_summary_parts)
        )
        
        db.session.add(new_order)
        db.session.commit()
        
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
            if transaction_status in ['capture', 'settlement']:
                order.status = 'Completed'
            elif transaction_status in ['cancel', 'deny', 'expire']:
                order.status = 'Canceled'
            elif transaction_status == 'pending':
                order.status = 'Pending'
            db.session.commit()
            
        return jsonify({"status": "ok"})
    except Exception as e:
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
    
    query_orders = Order.query.filter(Order.status == 'Completed')
    if selected_date:
        query_orders = query_orders.filter(db.func.date(Order.date) == selected_date)
    if selected_month:
        query_orders = query_orders.filter(db.func.strftime('%Y-%m', Order.date) == selected_month)
        
    total_revenue_query = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status == 'Completed')
    if selected_date:
        total_revenue_query = total_revenue_query.filter(db.func.date(Order.date) == selected_date)
    if selected_month:
        total_revenue_query = total_revenue_query.filter(db.func.strftime('%Y-%m', Order.date) == selected_month)
    total_revenue = total_revenue_query.scalar() or 0
    
    orders_count = query_orders.count()
    best_seller = Menu.query.order_by(Menu.reviews.desc()).first()
    
    # Calculate Product Performance by parsing Order.product_summary
    from collections import defaultdict
    category_sales = defaultdict(int)
    all_orders = query_orders.all()
    menus = {m.name: m.category for m in Menu.query.all()}
    
    total_items_sold = 0
    for order in all_orders:
        parts = order.product_summary.split(',')
        for part in parts:
            part = part.strip()
            if 'x ' in part:
                try:
                    qty_str, name = part.split('x ', 1)
                    qty = int(qty_str)
                    category = menus.get(name, 'Lainnya')
                    category_sales[category] += qty
                    total_items_sold += qty
                except:
                    pass
                    
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
    
    return render_template('admin_report.html',
                           total_revenue=total_revenue,
                           orders_count=orders_count,
                           best_seller=best_seller,
                           top_categories=top_categories,
                           recommended_focus=recommended_focus,
                           top_tables=tables,
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
