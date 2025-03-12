from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from extensions import init_db

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class Config:
    SQLURL = os.getenv('DATABASE_URL')  
    SQLALCHEMY_DATABASE_URI = SQLURL
    SQLALCHEMY_TRACK_MODIFICATIONS = False



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize the API
    # Swagger UI will be at /swagger
    # api = Api(app, doc='/swagger')  
    # api.add_namespace(users_ns)
    # api.add_namespace(clients_ns)
    # api.add_namespace(accounts_ns)

    init_db(app)

    return app

# Register Telegram Blueprint
from routes.telegram_api import telegram_blueprint
app.register_blueprint(telegram_blueprint, url_prefix="/telegram")

# Register Staff Blueprint (if you have one)
from routes.staff import staff_blueprint
app.register_blueprint(staff_blueprint, url_prefix="/api")

def init_db_and_run():
    app = create_app()    
    db.create_all()  # Creates all tables, but will be skipped if USE_DB is False
    
    # Run the app
    app.run(debug=True)

if __name__ == '__main__':
    init_db_and_run()

