from app.tools.billing import create_draft_bill, add_bill_item


# Create a draft bill
bill = create_draft_bill()

print("Created bill:")
print(bill)


# Add 2 kg sugar
item = add_bill_item(
    bill_id=bill["bill_id"],
    product_name="sugar",
    quantity=2
)

print("\nAdded item:")
print(item)