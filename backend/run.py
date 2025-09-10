from app import create_app
from app.extensions import db
from dotenv import load_dotenv
load_dotenv()

from app.services.auth_service import AuthService
print(AuthService.hash_password("12345678"))

app = create_app()
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    import os

    port = int(os.getenv("FLASK_RUN_PORT", "5050"))
    app.run(host="127.0.0.1", port=port, debug=True)


    from app.services.auth_service import AuthService
