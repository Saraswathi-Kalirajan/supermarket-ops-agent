from app.database import SessionLocal
from app.models import Customer


def create_customer(name: str, phone: str = None):
    db = SessionLocal()

    try:
        # Check if customer already exists
        existing = (
            db.query(Customer)
            .filter(Customer.name.ilike(name))
            .first()
        )

        if existing:
            return {
                "success": False,
                "message": f"Customer '{name}' already exists.",
                "customer_id": existing.id
            }

        customer = Customer(
            name=name,
            phone=phone
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return {
            "success": True,
            "message": "Customer created successfully.",
            "customer_id": customer.id,
            "name": customer.name,
            "phone": customer.phone
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()