from app.tools.khata import (
    add_credit,
    record_payment,
    get_balance
)


# 1. Add ₹500 credit to Ramesh
print("\n--- ADD CREDIT ---")

result = add_credit(
    customer_name="Ramesh",
    amount=500,
    description="Grocery credit"
)

print(result)


# 2. Check balance
print("\n--- CHECK BALANCE ---")

result = get_balance("Ramesh")

print(result)


# 3. Ramesh pays ₹300
print("\n--- RECORD PAYMENT ---")

result = record_payment(
    customer_name="Ramesh",
    amount=300,
    description="Partial payment"
)

print(result)


# 4. Check balance again
print("\n--- FINAL BALANCE ---")

result = get_balance("Ramesh")

print(result)