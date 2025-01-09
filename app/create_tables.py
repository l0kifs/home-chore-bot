from database import SessionManager
from domain.models import Chore, Person, Base

def init_db():
    # Access engine from SessionManager directly
    session_manager = SessionManager()
    Base.metadata.create_all(bind=session_manager.engine)

if __name__ == "__main__":
    init_db()
