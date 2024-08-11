# main.py

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler
from products.products import products_bp
from products.ormProducts import ormProducts_bp
from auth.auth import auth_bp
from auth.ormAuth import ormAuth_bp
from cron.cron import cron_bp
from config import init_db, init_mail, init_cloudinary, init_orm_db, Config
from flasgger import Swagger
app = Flask(__name__)
mongo = init_db(app)
app.mongo = mongo 
# app.config.from_object(Config)
# mongo = init_orm_db(app)
mail = init_mail(app)
jwt = JWTManager(app)
init_cloudinary(app)

swagger = Swagger(app)
# odm
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(cron_bp, url_prefix='/api/cron')

# orm
app.register_blueprint(ormAuth_bp, url_prefix='/api/auth/orm')
app.register_blueprint(ormProducts_bp, url_prefix='/api/products/orm')

if __name__ == '__main__':
    app.run(debug=True)

