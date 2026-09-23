from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    unit = Column(String(20), nullable=False)
    is_loose = Column(Boolean, nullable=False, default=False)

    cost_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)

    quantity = Column(Numeric(12, 3), nullable=False, default=0)
    reorder_level = Column(Numeric(12, 3), nullable=False, default=0)

    hsn_code = Column(String(20))
    gst_rate = Column(Numeric(5, 2), nullable=False, default=0)

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True)
    bill_number = Column(String(50), unique=True, nullable=False)

    subtotal = Column(Numeric(12, 2), nullable=False, default=0)
    cgst = Column(Numeric(12, 2), nullable=False, default=0)
    sgst = Column(Numeric(12, 2), nullable=False, default=0)
    total_tax = Column(Numeric(12, 2), nullable=False, default=0)
    grand_total = Column(Numeric(12, 2), nullable=False, default=0)

    payment_method = Column(String(20))
    payment_reference = Column(String(100))

    status = Column(String(20), nullable=False, default="draft")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True)

    bill_id = Column(
        Integer,
        ForeignKey("bills.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(Numeric(12, 3), nullable=False)

    unit_price = Column(Numeric(10, 2), nullable=False)

    gst_rate = Column(Numeric(5, 2), nullable=False)

    cgst = Column(Numeric(10, 2), nullable=False, default=0)
    sgst = Column(Numeric(10, 2), nullable=False, default=0)

    taxable_amount = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)  

# ============================================================
# KHATA / CUSTOMER CREDIT
# ============================================================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)

    name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    phone = Column(String(20))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class KhataTransaction(Base):
    __tablename__ = "khata_transactions"

    id = Column(Integer, primary_key=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    transaction_type = Column(
        String(20),
        nullable=False
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False
    )

    description = Column(String(255))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
