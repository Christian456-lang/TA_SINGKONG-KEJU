import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

tidb_host = os.getenv('TIDB_HOST')
tidb_port = os.getenv('TIDB_PORT')
tidb_user = os.getenv('TIDB_USER')
tidb_password = os.getenv('TIDB_PASSWORD')
tidb_db = os.getenv('TIDB_DATABASE')

DATABASE_URI = f"mysql+pymysql://{tidb_user}:{tidb_password}@{tidb_host}:{tidb_port}/{tidb_db}?ssl_verify_cert=true&ssl_verify_identity=true"

def optimize_database():
    print(f"Menghubungkan ke database: {tidb_host}...")
    engine = create_engine(DATABASE_URI)
    
    with engine.connect() as conn:
        print("Menambahkan index ke tabel `order`...")
        try:
            conn.execute(text("CREATE INDEX idx_order_status ON `order` (status);"))
            print("Berhasil menambahkan index pada `order.status`.")
        except Exception as e:
            print(f"Error atau index mungkin sudah ada: {e}")
            
        try:
            conn.execute(text("CREATE INDEX idx_order_date ON `order` (date);"))
            print("Berhasil menambahkan index pada `order.date`.")
        except Exception as e:
            print(f"Error atau index mungkin sudah ada: {e}")
            
        print("Menambahkan index ke tabel `menu`...")
        try:
            conn.execute(text("CREATE INDEX idx_menu_category ON menu (category);"))
            print("Berhasil menambahkan index pada `menu.category`.")
        except Exception as e:
            print(f"Error atau index mungkin sudah ada: {e}")
            
        try:
            conn.execute(text("CREATE INDEX idx_menu_group ON menu (`group`);"))
            print("Berhasil menambahkan index pada `menu.group`.")
        except Exception as e:
            print(f"Error atau index mungkin sudah ada: {e}")
            
        print("Selesai! Database telah dioptimasi.")

if __name__ == '__main__':
    optimize_database()
