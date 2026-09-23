from decimal import Decimal

from app.database import SessionLocal
from app.models import Customer, KhataTransaction


def get_customer_balance(db, customer_id):
    transactions = (
        db.query(KhataTransaction)
        .filter(KhataTransaction.customer_id == customer_id)
        .all()
    )

    balance = Decimal("0.00")

    for transaction in transactions:
        if transaction.transaction_type == "credit":
            balance += transaction.amount

        elif transaction.transaction_type == "payment":
            balance -= transaction.amount

    return balance


def add_credit(
    customer_name: str,
    amount: float,
    description: str = None
):
    db = SessionLocal()

    try:
        amount = Decimal(str(amount))

        if amount <= 0:
            return {
                "success": False,
                "message": "Credit amount must be greater than zero."
            }

        # Find customer
        customer = (
            db.query(Customer)
            .filter(Customer.name.ilike(customer_name))
            .first()
        )

        if not customer:
            return {
                "success": False,
                "message": f"Customer '{customer_name}' was not found."
            }

        # Create credit transaction
        transaction = KhataTransaction(
            customer_id=customer.id,
            transaction_type="credit",
            amount=amount,
            description=description
        )

        db.add(transaction)
        db.commit()

        # Calculate new balance
        balance = get_customer_balance(
            db,
            customer.id
        )

        return {
            "success": True,
            "message": "Credit added successfully.",
            "customer": customer.name,
            "amount": float(amount),
            "balance": float(balance)
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def record_payment(
    customer_name: str,
    amount: float,
    description: str = None
):
    db = SessionLocal()

    try:
        amount = Decimal(str(amount))

        if amount <= 0:
            return {
                "success": False,
                "message": "Payment amount must be greater than zero."
            }

        # Find customer
        customer = (
            db.query(Customer)
            .filter(Customer.name.ilike(customer_name))
            .first()
        )

        if not customer:
            return {
                "success": False,
                "message": f"Customer '{customer_name}' was not found."
            }

        # Calculate current balance
        current_balance = get_customer_balance(
            db,
            customer.id
        )

        # Prevent overpayment
        if amount > current_balance:
            return {
                "success": False,
                "message": (
                    f"Payment ₹{amount} is greater than "
                    f"{customer.name}'s outstanding balance "
                    f"of ₹{current_balance}."
                )
            }

        # Create payment transaction
        transaction = KhataTransaction(
            customer_id=customer.id,
            transaction_type="payment",
            amount=amount,
            description=description
        )

        db.add(transaction)
        db.commit()

        # Calculate new balance
        balance = get_customer_balance(
            db,
            customer.id
        )

        return {
            "success": True,
            "message": "Payment recorded successfully.",
            "customer": customer.name,
            "amount": float(amount),
            "balance": float(balance)
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_balance(customer_name: str):
    db = SessionLocal()

    try:
        # Find customer
        customer = (
            db.query(Customer)
            .filter(Customer.name.ilike(customer_name))
            .first()
        )

        if not customer:
            return {
                "success": False,
                "message": f"Customer '{customer_name}' was not found."
            }

        # Calculate balance from transactions
        balance = get_customer_balance(
            db,
            customer.id
        )

        return {
            "success": True,
            "customer": customer.name,
            "balance": float(balance)
        }

    finally:
        db.close()