import os
from app import app, db, Admin

with app.app_context():
    print("Dropping Admin table...")
    Admin.__table__.drop(db.engine, checkfirst=True)
    
    print("Creating Admin table...")
    Admin.__table__.create(db.engine, checkfirst=True)
    
    print("Inserting default users...")
    admin = Admin(username='admin', password='admin123', role='admin')
    kasir = Admin(username='kasir', password='kasir123', role='kasir')
    
    db.session.add(admin)
    db.session.add(kasir)
    db.session.commit()
    
    print("Admin table has been reset successfully.")
