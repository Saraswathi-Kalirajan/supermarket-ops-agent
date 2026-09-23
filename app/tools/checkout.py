from app.database import SessionLocal
from app.models import Customer

from app.tools.billing import (
    create_draft_bill,
    add_bill_item,
    finalize_bill,
)

from app.tools.khata import add_credit


def checkout(
    customer_name: str,
    product_name: str,
    quantity: float,
    payment_method: str
):
    db = SessionLocal()

    try:
        # 1. Find customer
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

        # 2. Validate payment method
        payment_method = payment_method.lower()

        allowed_methods = [
            "cash",
            "upi",
            "credit"
        ]

        if payment_method not in allowed_methods:
            return {
                "success": False,
                "message": (
                    "Invalid payment method. "
                    "Use cash, upi, or credit."
                )
            }

        # 3. Create draft bill
        bill_result = create_draft_bill()

        if not bill_result["success"]:
            return bill_result

        bill_id = bill_result["bill_id"]

        # 4. Add product to bill
        item_result = add_bill_item(
            bill_id=bill_id,
            product_name=product_name,
            quantity=quantity
        )

        if not item_result["success"]:
            return item_result

        # 5. Finalize bill
        final_result = finalize_bill(
            bill_id=bill_id,
            payment_method=payment_method
        )

        if not final_result["success"]:
            return final_result

        # 6. If payment is CREDIT,
        #    add the bill amount to customer's Khata
        if payment_method == "credit":

            credit_result = add_credit(
                customer_name=customer.name,
                amount=final_result["grand_total"],
                description=(
                    f"Credit purchase - "
                    f"{bill_result['bill_number']}"
                )
            )

            if not credit_result["success"]:
                return credit_result

        # 7. Return successful checkout
        return {
            "success": True,
            "message": "Checkout completed successfully.",
            "customer": customer.name,
            "bill_id": bill_id,
            "bill_number": bill_result["bill_number"],
            "payment_method": payment_method,
            "subtotal": final_result["subtotal"],
            "cgst": final_result["cgst"],
            "sgst": final_result["sgst"],
            "total_tax": final_result["total_tax"],
            "grand_total": final_result["grand_total"]
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()