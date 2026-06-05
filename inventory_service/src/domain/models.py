from dataclasses import dataclass

@dataclass
class Product:
    id: str
    sku: str
    available_quantity: int
    reserved_quantity: int
    
    def can_fulfill(self, requested_quantity: int) -> bool:
        """Business rule: Do we have enough stock?"""
        return self.available_quantity >= requested_quantity
        
    def reserve(self, quantity: int):
        """Business rule: Move stock from available to reserved."""
        if not self.can_fulfill(quantity):
            raise ValueError(f"Insufficient stock for SKU {self.sku}")
        self.available_quantity -= quantity
        self.reserved_quantity += quantity