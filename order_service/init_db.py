import sys
import os

# Ensure Python can find the 'src' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.database import engine, Base

def initialize_database():
    print("Connecting to PostgreSQL...")
    # This command inspects the ORM classes and creates the tables in the DB
    Base.metadata.create_all(bind=engine)
    print("Success: 'orders' and 'order_items' tables created in orders_db!")

if __name__ == "__main__":
    initialize_database()