from decimal import Decimal, ROUND_HALF_UP
import uuid

from app.database import SessionLocal
from app.models import Bill, BillItem, Product


# ============================================================
# 1. CREATE DRAFT BILL
# ============================================================

def create_draft_bill():
    db = SessionLocal()

    try:
        bill_number = "BILL-" + uuid.uuid4().hex[:8].upper()

        bill = Bill(
            bill_number=bill_number,
            status="draft"
        )

        db.add(bill)
        db.commit()
        db.refresh(bill)

        return {
            "success": True,
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "status": bill.status
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# 2. CALCULATE GST
# ============================================================

def calculate_gst(price, quantity, gst_rate):
    price = Decimal(str(price))
    quantity = Decimal(str(quantity))
    gst_rate = Decimal(str(gst_rate))

    taxable_amount = price * quantity

    total_tax = (
        taxable_amount * gst_rate / Decimal("100")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # Intra-state sale:
    # GST is split equally into CGST and SGST
    cgst = (
        total_tax / Decimal("2")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    sgst = total_tax - cgst

    total_amount = taxable_amount + total_tax

    return {
        "taxable_amount": taxable_amount,
        "cgst": cgst,
        "sgst": sgst,
        "total_tax": total_tax,
        "total_amount": total_amount
    }


# ============================================================
# 3. ADD ITEM TO DRAFT BILL
# ============================================================

def add_bill_item(
    bill_id: int,
    product_name: str,
    quantity: float
):
    db = SessionLocal()

    try:
        if quantity <= 0:
            return {
                "success": False,
                "message": "Quantity must be greater than zero."
            }

        # Find bill
        bill = (
            db.query(Bill)
            .filter(Bill.id == bill_id)
            .first()
        )

        if not bill:
            return {
                "success": False,
                "message": f"Bill {bill_id} was not found."
            }

        # Only draft bills can be modified
        if bill.status != "draft":
            return {
                "success": False,
                "message": "Items can only be added to a draft bill."
            }

        # Find product
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

        # Check stock
        if quantity > product.quantity:
            return {
                "success": False,
                "message": (
                    f"Only {product.quantity} {product.unit} "
                    f"of {product.name} is available."
                )
            }

        # Calculate GST
        tax = calculate_gst(
            product.selling_price,
            quantity,
            product.gst_rate
        )

        # Create bill item
        item = BillItem(
            bill_id=bill.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.selling_price,
            gst_rate=product.gst_rate,
            cgst=tax["cgst"],
            sgst=tax["sgst"],
            taxable_amount=tax["taxable_amount"],
            total_amount=tax["total_amount"]
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return {
            "success": True,
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "product": product.name,
            "quantity": quantity,
            "unit": product.unit,
            "unit_price": float(product.selling_price),
            "gst_rate": float(product.gst_rate),
            "taxable_amount": float(tax["taxable_amount"]),
            "cgst": float(tax["cgst"]),
            "sgst": float(tax["sgst"]),
            "total_tax": float(tax["total_tax"]),
            "total_amount": float(tax["total_amount"])
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# 4. GET BILL SUMMARY
# ============================================================

def get_bill_summary(bill_id: int):
    db = SessionLocal()

    try:
        # Find bill
        bill = (
            db.query(Bill)
            .filter(Bill.id == bill_id)
            .first()
        )

        if not bill:
            return {
                "success": False,
                "message": f"Bill {bill_id} was not found."
            }

        # Get bill items with products
        items = (
            db.query(BillItem, Product)
            .join(
                Product,
                BillItem.product_id == Product.id
            )
            .filter(BillItem.bill_id == bill_id)
            .all()
        )

        result_items = []

        subtotal = Decimal("0")
        total_cgst = Decimal("0")
        total_sgst = Decimal("0")
        total_tax = Decimal("0")
        grand_total = Decimal("0")

        for item, product in items:

            subtotal += item.taxable_amount
            total_cgst += item.cgst
            total_sgst += item.sgst
            total_tax += item.cgst + item.sgst
            grand_total += item.total_amount

            result_items.append({
                "product": product.name,
                "quantity": float(item.quantity),
                "unit": product.unit,
                "unit_price": float(item.unit_price),
                "gst_rate": float(item.gst_rate),
                "taxable_amount": float(item.taxable_amount),
                "cgst": float(item.cgst),
                "sgst": float(item.sgst),
                "total_amount": float(item.total_amount)
            })

        return {
            "success": True,
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "status": bill.status,
            "items": result_items,
            "subtotal": float(subtotal),
            "cgst": float(total_cgst),
            "sgst": float(total_sgst),
            "total_tax": float(total_tax),
            "grand_total": float(grand_total)
        }

    finally:
        db.close()


# ============================================================
# 5. REMOVE ITEM FROM DRAFT BILL
# ============================================================

def remove_bill_item(
    bill_id: int,
    product_name: str
):
    db = SessionLocal()

    try:
        # Find bill
        bill = (
            db.query(Bill)
            .filter(Bill.id == bill_id)
            .first()
        )

        if not bill:
            return {
                "success": False,
                "message": f"Bill {bill_id} was not found."
            }

        if bill.status != "draft":
            return {
                "success": False,
                "message": "Only draft bills can be edited."
            }

        # Find product
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

        # Find item in bill
        item = (
            db.query(BillItem)
            .filter(
                BillItem.bill_id == bill_id,
                BillItem.product_id == product.id
            )
            .first()
        )

        if not item:
            return {
                "success": False,
                "message": f"{product.name} is not in this bill."
            }

        db.delete(item)
        db.commit()

        return {
            "success": True,
            "message": f"{product.name} removed from the bill.",
            "bill_id": bill_id,
            "product": product.name
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# 6. UPDATE ITEM QUANTITY
# ============================================================

def update_bill_item(
    bill_id: int,
    product_name: str,
    new_quantity: float
):
    db = SessionLocal()

    try:
        if new_quantity <= 0:
            return {
                "success": False,
                "message": "Quantity must be greater than zero."
            }

        # Find bill
        bill = (
            db.query(Bill)
            .filter(Bill.id == bill_id)
            .first()
        )

        if not bill:
            return {
                "success": False,
                "message": f"Bill {bill_id} was not found."
            }

        if bill.status != "draft":
            return {
                "success": False,
                "message": "Only draft bills can be edited."
            }

        # Find product
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

        # Find bill item
        item = (
            db.query(BillItem)
            .filter(
                BillItem.bill_id == bill_id,
                BillItem.product_id == product.id
            )
            .first()
        )

        if not item:
            return {
                "success": False,
                "message": f"{product.name} is not in this bill."
            }

        # Remember old quantity
        old_quantity = float(item.quantity)

        # Check available stock
        if new_quantity > product.quantity:
            return {
                "success": False,
                "message": (
                    f"Only {product.quantity} {product.unit} "
                    f"of {product.name} is available."
                )
            }

        # Recalculate GST
        tax = calculate_gst(
            product.selling_price,
            new_quantity,
            product.gst_rate
        )

        # Update item
        item.quantity = new_quantity
        item.unit_price = product.selling_price
        item.gst_rate = product.gst_rate
        item.cgst = tax["cgst"]
        item.sgst = tax["sgst"]
        item.taxable_amount = tax["taxable_amount"]
        item.total_amount = tax["total_amount"]

        db.commit()
        db.refresh(item)

        return {
            "success": True,
            "product": product.name,
            "old_quantity": old_quantity,
            "new_quantity": new_quantity,
            "taxable_amount": float(tax["taxable_amount"]),
            "cgst": float(tax["cgst"]),
            "sgst": float(tax["sgst"]),
            "total_tax": float(tax["total_tax"]),
            "total_amount": float(tax["total_amount"])
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()  

# ============================================================
# 7. FINALIZE BILL
# ============================================================

def finalize_bill(
    bill_id: int,
    payment_method: str = "UPI",
    payment_reference: str | None = None
):
    db = SessionLocal()

    try:
        # ----------------------------------------------------
        # Find the bill
        # ----------------------------------------------------

        bill = (
            db.query(Bill)
            .filter(Bill.id == bill_id)
            .with_for_update()
            .first()
        )

        if not bill:
            return {
                "success": False,
                "message": f"Bill {bill_id} was not found."
            }

        # ----------------------------------------------------
        # IDEMPOTENCY
        # If already finalized, do not bill again.
        # ----------------------------------------------------

        if bill.status == "finalized":
            return {
                "success": True,
                "message": "Bill was already finalized.",
                "bill_id": bill.id,
                "bill_number": bill.bill_number,
                "status": bill.status
            }

        # ----------------------------------------------------
        # Only draft bills can be finalized
        # ----------------------------------------------------

        if bill.status != "draft":
            return {
                "success": False,
                "message": (
                    f"Bill cannot be finalized because its "
                    f"status is '{bill.status}'."
                )
            }

        # ----------------------------------------------------
        # Validate payment method
        # ----------------------------------------------------

        allowed_methods = {
            "cash",
            "upi",
            "credit"
        }

        payment_method = payment_method.lower()

        if payment_method not in allowed_methods:
            return {
                "success": False,
                "message": (
                    "Payment method must be Cash, UPI, or Card."
                )
            }

        # ----------------------------------------------------
        # Get all bill items
        # ----------------------------------------------------

        items = (
            db.query(BillItem)
            .filter(BillItem.bill_id == bill_id)
            .all()
        )

        if not items:
            return {
                "success": False,
                "message": "Cannot finalize an empty bill."
            }

        # ----------------------------------------------------
        # FIRST: Check ALL stock
        #
        # We check everything before changing anything.
        # This prevents partial stock deduction.
        # ----------------------------------------------------

        products = {}

        for item in items:

            product = (
                db.query(Product)
                .filter(Product.id == item.product_id)
                .with_for_update()
                .first()
            )

            if not product:
                db.rollback()

                return {
                    "success": False,
                    "message": (
                        f"Product ID {item.product_id} "
                        f"was not found."
                    )
                }

            products[item.product_id] = product

            # Oversell protection
            if item.quantity > product.quantity:
                db.rollback()

                return {
                    "success": False,
                    "message": (
                        f"Cannot finalize bill. "
                        f"Only {product.quantity} "
                        f"{product.unit} of {product.name} "
                        f"is available, but the bill requires "
                        f"{item.quantity}."
                    )
                }

            # ------------------------------------------------
            # Don't sell below cost
            # ------------------------------------------------

            if item.unit_price < product.cost_price:
                db.rollback()

                return {
                    "success": False,
                    "message": (
                        f"Cannot sell {product.name} below "
                        f"its cost price."
                    )
                }

        # ----------------------------------------------------
        # ALL checks passed.
        #
        # Now reduce stock.
        # ----------------------------------------------------

        for item in items:

            product = products[item.product_id]

            product.quantity -= item.quantity

        # ----------------------------------------------------
        # Save payment information
        # ----------------------------------------------------

        bill.payment_method = payment_method
        bill.payment_reference = payment_reference

        # ----------------------------------------------------
        # Calculate final totals
        # ----------------------------------------------------

        subtotal = Decimal("0")
        total_cgst = Decimal("0")
        total_sgst = Decimal("0")
        total_tax = Decimal("0")
        grand_total = Decimal("0")

        for item in items:

            subtotal += item.taxable_amount
            total_cgst += item.cgst
            total_sgst += item.sgst
            total_tax += item.cgst + item.sgst
            grand_total += item.total_amount

        # ----------------------------------------------------
        # Store totals
        # ----------------------------------------------------

        bill.subtotal = subtotal
        bill.cgst = total_cgst
        bill.sgst = total_sgst
        bill.total_tax = total_tax
        bill.grand_total = grand_total

        # ----------------------------------------------------
        # Mark bill as finalized
        # ----------------------------------------------------

        bill.status = "finalized"

        db.commit()

        return {
            "success": True,
            "message": "Bill finalized successfully.",
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "status": bill.status,
            "payment_method": payment_method,
            "payment_reference": payment_reference,
            "subtotal": float(subtotal),
            "cgst": float(total_cgst),
            "sgst": float(total_sgst),
            "total_tax": float(total_tax),
            "grand_total": float(grand_total)
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close() 


