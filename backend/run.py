# run.py
from app import create_app
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_RUN_PORT", "5050"))
    app.run(host="127.0.0.1", port=port, debug=True)