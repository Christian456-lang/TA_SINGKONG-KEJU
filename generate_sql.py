import os
import sys

# Tambahkan current path ke sys.path supaya bisa import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import UNGGULAN, MAKANAN_BERAT, MAKANAN_RINGAN, MINUMAN
except ImportError:
    print("Gagal mengimpor data dari app.py")
    sys.exit(1)

def escape_sql_string(val):
    if val is None:
        return 'NULL'
    if isinstance(val, str):
        # Escape single quotes
        val = val.replace("'", "''")
        return f"'{val}'"
    return str(val)

sql = []
sql.append("CREATE TABLE IF NOT EXISTS menu (")
sql.append("    id INT AUTO_INCREMENT PRIMARY KEY,")
sql.append("    name VARCHAR(100) NOT NULL,")
sql.append("    category VARCHAR(50) NOT NULL,")
sql.append("    description TEXT,")
sql.append("    price INT NOT NULL,")
sql.append("    rating FLOAT DEFAULT 0.0,")
sql.append("    reviews INT DEFAULT 0,")
sql.append("    image VARCHAR(255) NOT NULL,")
sql.append("    `group` VARCHAR(50) NOT NULL,")
sql.append("    stock INT DEFAULT 100")
sql.append(");")
sql.append("")
sql.append("TRUNCATE TABLE menu;")
sql.append("")
sql.append("DROP TABLE IF EXISTS admin;")
sql.append("CREATE TABLE IF NOT EXISTS admin (")
sql.append("    id INT AUTO_INCREMENT PRIMARY KEY,")
sql.append("    username VARCHAR(50) NOT NULL UNIQUE,")
sql.append("    password VARCHAR(255) NOT NULL,")
sql.append("    role VARCHAR(20) DEFAULT 'admin'")
sql.append(");")
sql.append("")
sql.append("INSERT IGNORE INTO admin (username, password, role) VALUES ('admin', 'admin123', 'admin');")
sql.append("INSERT IGNORE INTO admin (username, password, role) VALUES ('kasir', 'kasir123', 'kasir');")
sql.append("")
sql.append("CREATE TABLE IF NOT EXISTS `order` (")
sql.append("    id INT AUTO_INCREMENT PRIMARY KEY,")
sql.append("    order_id VARCHAR(20) NOT NULL UNIQUE,")
sql.append("    table_number VARCHAR(10) NOT NULL,")
sql.append("    table_category VARCHAR(20) NOT NULL,")
sql.append("    date DATETIME NOT NULL,")
sql.append("    total_amount INT NOT NULL,")
sql.append("    status VARCHAR(20) NOT NULL,")
sql.append("    product_summary VARCHAR(255) NOT NULL")
sql.append(");")
sql.append("")

def generate_inserts(data_list, group_name):
    for item in data_list:
        name = escape_sql_string(item.get('name'))
        category = escape_sql_string(item.get('category'))
        desc = escape_sql_string(item.get('description', ''))
        price = item.get('price', 0)
        rating = item.get('rating', 0.0)
        reviews = item.get('reviews', 0)
        image = escape_sql_string(item.get('image', ''))
        grp = escape_sql_string(group_name)
        
        sql.append(f"INSERT INTO menu (name, category, description, price, rating, reviews, image, `group`, stock) VALUES ({name}, {category}, {desc}, {price}, {rating}, {reviews}, {image}, {grp}, 100);")

generate_inserts(UNGGULAN, 'unggulan')
generate_inserts(MAKANAN_BERAT, 'makanan_berat')
generate_inserts(MAKANAN_RINGAN, 'makanan_ringan')
generate_inserts(MINUMAN, 'minuman')

with open('database.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql))

print("File database.sql berhasil dibuat!")
