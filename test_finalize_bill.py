from app.tools.billing import (
    create_draft_bill,
    add_bill_item,
    get_bill_summary,
    finalize_bill
)


# ----------------------------------------
# 1. Create a draft bill
# ----------------------------------------

bill = create_draft_bill()

print("CREATED BILL:")
print(bill)

bill_id = bill["bill_id"]


# ----------------------------------------
# 2. Add items
# ----------------------------------------

print("\nADDING MAGGI:")

print(
    add_bill_item(
        bill_id=bill_id,
        product_name="Maggi",
        quantity=2
    )
)


print("\nADDING SUGAR:")

print(
    add_bill_item(
        bill_id=bill_id,
        product_name="Sugar",
        quantity=2
    )
)


# ----------------------------------------
# 3. Show draft bill
# ----------------------------------------

print("\nDRAFT BILL:")

print(
    get_bill_summary(bill_id)
)


# ----------------------------------------
# 4. Finalize bill
# ----------------------------------------

print("\nFINALIZING BILL:")

result = finalize_bill(
    bill_id=bill_id,
    payment_method="UPI",
    payment_reference="UPI-TEST-001"
)

print(result)


# ----------------------------------------
# 5. Show final bill
# ----------------------------------------

print("\nFINAL BILL:")

print(
    get_bill_summary(bill_id)
)