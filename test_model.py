from app.database import SessionLocal
from app.models import Product


db = SessionLocal()

try:
    products = db.query(Product).all()

    for product in products:
        print(
            product.id,
            product.name,
            product.quantity,
            product.selling_price
        )

finally:
    db.close()