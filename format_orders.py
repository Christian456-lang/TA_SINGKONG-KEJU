import re
from app import app, db, Order, Menu

with app.app_context():
    orders = Order.query.all()
    updated = 0
    for order in orders:
        if '(x' in order.product_summary:
            new_parts = []
            for part in order.product_summary.split(','):
                part = part.strip()
                if '(x' in part:
                    match = re.search(r'(.+?) \(x(\d+)\)', part)
                    if match:
                        name = match.group(1).strip()
                        qty = match.group(2)
                        if name == 'Kroket': name = 'Kroket Singkong D9'
                        elif name == 'Singkong Keju': name = 'Singkong Keju D9'
                        elif name == 'Getuk D9 Mix': name = 'Getuk D9 Pelangi'
                        new_parts.append(f'{qty}x {name}')
                    else:
                        new_parts.append(part)
                else:
                    new_parts.append(part)
            order.product_summary = ', '.join(new_parts)
            updated += 1
            
    db.session.commit()
    print('Updated product_summary in', updated, 'orders')
