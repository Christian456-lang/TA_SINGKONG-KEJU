from app import app, db, Order, Menu
with app.app_context():
    orders = Order.query.filter_by(status='Pending').all()
    print("Pending Orders:")
    for order in orders:
        items = []
        for part in order.product_summary.split(','):
            part = part.strip()
            if 'x ' in part:
                qty_str, name = part.split('x ', 1)
                menu = Menu.query.filter_by(name=name).first()
                if menu:
                    items.append(f"{qty_str}x {menu.name}")
                else:
                    items.append(f"MISSING({name})")
        print(f"- {order.order_id}: {items}")
