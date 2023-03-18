from app import app, db
from app.models import User, Picture

def init_db():
    with app.app_context():
        db.create_all()

    # Add any other initialization code here

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
