from infrastructure.telegram_bot import main
from database import init_db

# This will create the tables in the database
init_db()

if __name__ == "__main__":
    main()