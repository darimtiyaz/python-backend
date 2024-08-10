import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask_mail import Mail
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Load environment variables from a .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_COOKIE_CSRF_PROTECT = False  # Set to True in production for better security

    # Flask-Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = os.getenv('MAIL_PORT', 587)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', False)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')

    CLOUD_NAME=os.getenv('CLOUD_NAME'),
    API_KEY=os.getenv('API_KEY'),
    API_SECRET=os.getenv('API_SECRET')

def init_db(app):
    app.config.from_object(Config)
    mongo = PyMongo(app)
    return mongo

def init_mail(app):
    mail = Mail(app)
    return mail

def init_cloudinary(app):
    cloudinary.config(
        cloud_name=app.config['CLOUD_NAME'],
        api_key=app.config['API_KEY'],
        api_secret=app.config['API_SECRET']
)
