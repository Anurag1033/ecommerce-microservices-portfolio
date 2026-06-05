from src.infrastructure.database import SessionLocal, ProductORM
from src.infrastructure.redis_lock import acquire_product_lock

def process_order_created_event(event_data: dict):
    """
    Consumes the order data, acquires a lock, and updates inventory.
    """
    order_id = event_data.get('id')
    items = event_data.get('items', [])
    
    session = SessionLocal()
    try:
        for item in items:
            product_id = item['product_id']
            requested_qty = item['quantity']
            
            # 1. Acquire Distributed Lock for this specific product
            with acquire_product_lock(product_id):
                
                # 2. Fetch the product from the database
                product_orm = session.query(ProductORM).filter(ProductORM.id == product_id).first()
                if not product_orm:
                    raise ValueError(f"Product {product_id} not found in inventory")
                
                # 3. Map to Domain model to run business rules
                domain_product = product_orm.to_domain()
                
                # 4. Execute pure business logic (will raise ValueError if out of stock)
                domain_product.reserve(requested_qty)
                
                # 5. Map back to ORM and prepare for saving
                product_orm.available_quantity = domain_product.available_quantity
                product_orm.reserved_quantity = domain_product.reserved_quantity
                
        # 6. Commit the transaction for all items in the order
        session.commit()
        print(f"✅ Successfully reserved inventory for Order: {order_id}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Failed to reserve inventory for Order {order_id}: {str(e)}")
        # In a complete Saga, you would publish an 'InventoryFailed' event back to Kafka here
    finally:
        session.close()