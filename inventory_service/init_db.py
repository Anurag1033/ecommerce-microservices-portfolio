import sys
import os

# Ensure Python can find the 'src' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.database import engine, Base, SessionLocal, ProductORM

def initialize_database():
    print("Connecting to PostgreSQL inventory_db...")
    Base.metadata.create_all(bind=engine)
    print("Success: 'products' table created in inventory_db!")
    
    session = SessionLocal()
    # Check if the database is already seeded
    if session.query(ProductORM).count() == 0:
        print("Seeding initial inventory...")
        # Seeding 'prod-1' to match your Order Service test payload
        prod1 = ProductORM(id="prod-1", sku="MACBOOK-PRO", available_quantity=100, reserved_quantity=0)
        prod2 = ProductORM(id="prod-2", sku="LOGITECH-MOUSE", available_quantity=50, reserved_quantity=0)
        
        session.add_all([prod1, prod2])
        session.commit()
        print("Success: Seed data inserted!")
    else:
        print("Database already seeded. Skipping insertion.")
        
    session.close()

if __name__ == "__main__":
    initialize_database()