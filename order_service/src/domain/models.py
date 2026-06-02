from dataclasses import dataclass
from typing import List
from datetime import datetime
from enum import Enum

# Ensure this class is at the very top!
class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    price: float

@dataclass
class Order:
    id: str
    customer_id: str
    items: List[OrderItem]
    status: OrderStatus
    total_amount: float
    created_at: datetime
    
    @classmethod
    def create_new(cls, id: str, customer_id: str, items: List[OrderItem]) -> 'Order':
        """Business logic for creating a fresh order"""
        total = sum(item.quantity * item.price for item in items)
        if total <= 0:
            raise ValueError("Order total must be greater than zero")
            
        return cls(
            id=id,
            customer_id=customer_id,
            items=items,
            status=OrderStatus.PENDING,
            total_amount=total,
            created_at=datetime.utcnow()
        )
    
    def mark_confirmed(self):
        self.status = OrderStatus.CONFIRMED

    def mark_failed(self):
        self.status = OrderStatus.FAILED