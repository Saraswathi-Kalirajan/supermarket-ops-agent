from app.database import Base, engine
from app.models import Product, Bill, BillItem


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")