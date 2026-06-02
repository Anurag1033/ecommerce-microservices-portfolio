from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import uuid

from src.config import Config
from src.domain.models import OrderStatus, Order, OrderItem

# 1. Engine & Session Setup
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. SQLAlchemy ORM Models
class OrderItemORM(Base):
    __tablename__ = 'order_items'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey('orders.id'))
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

class OrderORM(Base):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Cascade deletes: If an order is deleted, its items are deleted too
    items = relationship("OrderItemORM", backref="order", cascade="all, delete-orphan")

    # 3. Clean Architecture Mappers
    def to_domain(self) -> Order:
        """Converts the SQLAlchemy object back into a pure Domain entity."""
        domain_items = [
            OrderItem(product_id=i.product_id, quantity=i.quantity, price=i.price)
            for i in self.items
        ]
        return Order(
            id=self.id,
            customer_id=self.customer_id,
            items=domain_items,
            status=self.status,
            total_amount=self.total_amount,
            created_at=self.created_at
        )
        
    @staticmethod
    def from_domain(order: Order) -> 'OrderORM':
        """Converts a pure Domain entity into a SQLAlchemy object for saving."""
        return OrderORM(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at,
            items=[
                OrderItemORM(product_id=item.product_id, quantity=item.quantity, price=item.price) 
                for item in order.items
            ]
        )