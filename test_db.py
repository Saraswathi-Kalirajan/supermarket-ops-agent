from sqlalchemy import text

from app.database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database()")
        )

        database_name = result.scalar()

        print("Connected successfully!")
        print("Database:", database_name)

except Exception as e:
    print("Database connection failed!")
    print(e)