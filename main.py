# from flask import Flask
# from flask_pymongo import PyMongo

# app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
# mongo = PyMongo(app)

# main.py

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler
from products.products import products_bp
from auth.auth import auth_bp
from cron.cron import cron_bp
from config import init_db, init_mail, init_cloudinary, Config

app = Flask(__name__)
mongo = init_db(app)
app.mongo = mongo 
mail = init_mail(app)
jwt = JWTManager(app)
init_cloudinary(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(cron_bp, url_prefix='/api/cron')


if __name__ == '__main__':
    app.run(debug=True)

