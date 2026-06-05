from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid

from src.config import Config
from src.domain.models import Product

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProductORM(Base):
    __tablename__ = 'products'
    
    # We allow manual ID insertion here so we can seed specific test data
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sku = Column(String, unique=True, nullable=False)
    available_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)

    def to_domain(self) -> Product:
        return Product(
            id=self.id,
            sku=self.sku,
            available_quantity=self.available_quantity,
            reserved_quantity=self.reserved_quantity
        )

    @staticmethod
    def from_domain(product: Product) -> 'ProductORM':
        return ProductORM(
            id=product.id,
            sku=product.sku,
            available_quantity=product.available_quantity,
            reserved_quantity=product.reserved_quantity
        )