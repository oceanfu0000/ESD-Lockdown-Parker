from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env
class Config:
    # Replace these values with your actual Aurora connection details
    SQLURL = os.getenv('DATABASE_URL')  
    SQLALCHEMY_DATABASE_URI = SQLURL
    SQLALCHEMY_TRACK_MODIFICATIONS = False