import random
from datetime import datetime, timedelta
from app import app, db, Order, Menu

def seed_orders():
    with app.app_context():
        # Clear existing orders
        Order.query.delete()
        
        menus = Menu.query.all()
        if not menus:
            print("No menus found. Please initialize database first.")
            return

        statuses = ['Completed', 'Processed', 'Canceled', 'Pending']
        tables = [('01', 'VIP'), ('15', 'VIP'), ('20', 'Regular'), ('05', 'Regular'), ('08', 'Regular')]
        
        now = datetime.now()
        
        for i in range(1, 51):
            # Pick 1 to 3 random menu items
            num_items = random.randint(1, 3)
            selected_menus = random.sample(menus, num_items)
            
            product_parts = []
            total = 0
            
            for menu in selected_menus:
                qty = random.randint(1, 4)
                product_parts.append(f"{qty}x {menu.name}")
                total += qty * menu.price
                
            tax = round(total * 0.1)
            total_amount = total + tax
            
            order = Order(
                order_id=f"ORD-{89000 + i}",
                table_number=random.choice(tables)[0],
                table_category=random.choice(tables)[1],
                date=now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 24), minutes=random.randint(0, 60)),
                total_amount=total_amount,
                status=random.choice(statuses),
                product_summary=', '.join(product_parts)
            )
            db.session.add(order)
            
        db.session.commit()
        print("Successfully seeded 50 realistic orders!")

if __name__ == '__main__':
    seed_orders()
