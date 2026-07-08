import os
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text('ALTER TABLE menu ADD COLUMN updated_at DATETIME'))
        db.session.commit()
        print("Column updated_at added successfully.")
    except Exception as e:
        print("Error adding column (it might already exist):", e)
