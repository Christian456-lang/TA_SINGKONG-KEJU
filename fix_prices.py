from app import app, db, Order, Menu

with app.app_context():
    orders = Order.query.all()
    updated = 0
    for order in orders:
        total = 0
        for part in order.product_summary.split(','):
            part = part.strip()
            if 'x ' in part:
                qty, name = part.split('x ', 1)
                menu = Menu.query.filter_by(name=name).first()
                if menu:
                    total += int(qty) * menu.price
        
        if total > 0:
            tax = round(total * 0.1)
            new_total = total + tax
            if order.total_amount != new_total:
                order.total_amount = new_total
                updated += 1
                
    db.session.commit()
    print(f"Updated {updated} orders")
