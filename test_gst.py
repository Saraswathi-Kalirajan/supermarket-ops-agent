from app.tools.billing import calculate_gst


result = calculate_gst(
    price=62,
    quantity=1,
    gst_rate=12
)

print(result)