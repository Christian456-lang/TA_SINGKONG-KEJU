from app import app, db, Admin, bcrypt

with app.app_context():
    admin = Admin.query.filter_by(username='admin').first()
    if admin:
        admin.password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        print("Admin password hashed.")
    
    kasir = Admin.query.filter_by(username='kasir').first()
    if kasir:
        kasir.password = bcrypt.generate_password_hash('kasir123').decode('utf-8')
        print("Kasir password hashed.")
        
    db.session.commit()
    print("Passwords updated successfully!")
