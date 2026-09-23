from app.tools.billing import (
    create_draft_bill,
    add_bill_item,
    remove_bill_item,
    update_bill_item,
    get_bill_summary
)


# Create bill
bill = create_draft_bill()

bill_id = bill["bill_id"]

print("Created:")
print(bill)


# Add Maggi
add_bill_item(
    bill_id=bill_id,
    product_name="Maggi",
    quantity=4
)

# Add Sugar
add_bill_item(
    bill_id=bill_id,
    product_name="Sugar",
    quantity=2
)

print("\nBEFORE EDIT:")
print(get_bill_summary(bill_id))


# Change Maggi from 4 -> 6
print("\nUPDATING MAGGI:")
print(
    update_bill_item(
        bill_id=bill_id,
        product_name="Maggi",
        new_quantity=6
    )
)


# Remove Sugar
print("\nREMOVING SUGAR:")
print(
    remove_bill_item(
        bill_id=bill_id,
        product_name="Sugar"
    )
)


print("\nAFTER EDIT:")
print(get_bill_summary(bill_id))