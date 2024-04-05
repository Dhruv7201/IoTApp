from app import app, dev
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    app.run(host=host, port=port, debug=dev)