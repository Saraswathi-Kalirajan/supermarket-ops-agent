from app.tools.billing import (
    create_draft_bill,
    add_bill_item,
    get_bill_summary
)


# Create a new bill
bill = create_draft_bill()

print("Created bill:")
print(bill)


# Add Sugar
add_bill_item(
    bill_id=bill["bill_id"],
    product_name="Sugar",
    quantity=2
)


# Add Maggi
add_bill_item(
    bill_id=bill["bill_id"],
    product_name="Maggi",
    quantity=4
)


# Show complete bill
summary = get_bill_summary(
    bill_id=bill["bill_id"]
)

print("\nBILL SUMMARY:")
print(summary)