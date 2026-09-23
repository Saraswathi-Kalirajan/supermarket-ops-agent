from decimal import Decimal
from app.database import SessionLocal
from app.models import Product



def get_stock(product_name: str):
    db = SessionLocal()

    try:
        product = (
            db.query(Product)
            .filter(Product.name.ilike(f"%{product_name}%"))
            .first()
        )

        if not product:
            return {
                "success": False,
                "message": f"Product '{product_name}' was not found."
            }

        return {
            "success": True,
            "product": product.name,
            "quantity": float(product.quantity),
            "unit": product.unit,
            "selling_price": float(product.selling_price),
            "reorder_level": float(product.reorder_level)
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def receive_stock(product_name: str, quantity: float):
    db = SessionLocal()

    try:
        product = (
            db.query(Product)
            .filter(Product.name.ilike(f"%{product_name}%"))
            .first()
        )

        if not product:
            return {
                "success": False,
                "message": f"Product '{product_name}' was not found."
            }

        if quantity <= 0:
            return {
                "success": False,
                "message": "Quantity must be greater than zero."
            }

        # Convert incoming quantity to Decimal
        # because database quantity is Decimal.
        quantity = Decimal(str(quantity))

        old_quantity = product.quantity

        product.quantity = product.quantity + quantity

        db.commit()
        db.refresh(product)

        return {
            "success": True,
            "product": product.name,
            "old_quantity": float(old_quantity),
            "received": float(quantity),
            "new_quantity": float(product.quantity),
            "unit": product.unit
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()



def get_low_stock():
    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(Product.quantity <= Product.reorder_level)
            .all()
        )

        result = []

        for product in products:
            result.append({
                "product": product.name,
                "quantity": float(product.quantity),
                "reorder_level": float(product.reorder_level),
                "unit": product.unit
            })

        return {
            "success": True,
            "count": len(result),
            "items": result
        }

    finally:
        db.close() 

