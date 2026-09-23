from app.tools.billing import (
    create_draft_bill,
    add_bill_item,
    finalize_bill
)

# Create bill
bill = create_draft_bill()

bill_id = bill["bill_id"]

print("BILL:")
print(bill)


# Try to add more Maggi than available
print("\nTRYING TO ADD 1000 MAGGI:")

result = add_bill_item(
    bill_id=bill_id,
    product_name="Maggi",
    quantity=1000
)

print(result)


# Try to finalize
print("\nTRYING TO FINALIZE:")

result = finalize_bill(
    bill_id=bill_id,
    payment_method="UPI",
    payment_reference="OVERSOLD-TEST"
)

print(result)