import uuid
from src.domain.models import Order, OrderItem
from src.infrastructure.database import SessionLocal, OrderORM
from src.infrastructure.kafka_prod import publish_order_created_event

def create_order(customer_id: str, items_data: list) -> dict:
    """
    Orchestrates the creation of an order:
    1. Creates the Domain entity (validates business rules)
    2. Saves to Postgres via ORM
    3. Publishes event to Kafka
    """
    # 1. Map raw data to Domain objects
    order_items = [OrderItem(**item) for item in items_data]
    new_order_id = str(uuid.uuid4())
    
    # Domain logic executes here (e.g., total > 0 validation)
    domain_order = Order.create_new(id=new_order_id, customer_id=customer_id, items=order_items)
    
    # 2. Save to Database
    session = SessionLocal()
    try:
        orm_order = OrderORM.from_domain(domain_order)
        session.add(orm_order)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

    # 3. Publish to Kafka
    order_dict = {
        "event_type": "OrderCreated",
        "id": domain_order.id,
        "customer_id": domain_order.customer_id,
        "status": domain_order.status.value,
        "total_amount": domain_order.total_amount,
        "items": [{"product_id": i.product_id, "quantity": i.quantity} for i in domain_order.items]
    }
    publish_order_created_event(order_dict)
    
    return order_dict