from app.tools.checkout import checkout


result = checkout(
    customer_name="Ramesh",
    product_name="Maggi",
    quantity=2,
    payment_method="cash"
)

print(result)