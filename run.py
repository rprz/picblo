from app import app, db
from app.models import User, Picture

def create_db():
    db.create_all()

if __name__ == '__main__':
    create_db()
    app.run()
