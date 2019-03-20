from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from time import strftime
from datetime import timedelta
import json, logging
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import JWTManager

#  ===== Flask =====
app = Flask(__name__)

# ===== Flask-RESTful =====
api = Api(app, catch_all_404s=True)

# ===== SQLAlchemy =====
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://danu:@172.31.46.60:3306/eCommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

# ===== Migrate =====
migrate = Migrate(app, db)

# ===== Manager =====
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# ===== Middlewares ======
@app.after_request
def after_request(response):
    if request.method=='GET':
        app.logger.warning("REQUEST_LOG\t%s %s", json.dumps, request.method, request.url, ({ 'request': request.args.to_dict(), 'response': json.loads(response.data.decode('utf-8')) }))
    else:
        app.logger.warning("REQUEST_LOG\t%s %s", json.dumps, request.method, request.url, ({ 'request': request.get_json(), 'response': json.loads(response.data.decode('utf-8')) }))
    return response

#  ===== Call blueprints =====
from blueprints.auth.__init__ import bp_auth # Folder auth
from blueprints.client.resources import bp_client # Folder client
from blueprints.admin.resources import bp_admin # Folder admin
from blueprints.users.resources import bp_user # Folder user
from blueprints.barang.resources import bp_barang # Folder barang
from blueprints.cart.resources import bp_cart # Folder cart
from blueprints.transaction.resources import bp_transaction # Folder transaction

# ===== Register blueprint =====
app.register_blueprint(bp_auth, url_prefix='/auth') # Folder auth
app.register_blueprint(bp_client, url_prefix='/client') # Folder client
app.register_blueprint(bp_admin, url_prefix='/admin') # Folder admin
app.register_blueprint(bp_user, url_prefix='/user') # Folder user
app.register_blueprint(bp_barang, url_prefix='/barang') # Folder barang
app.register_blueprint(bp_cart, url_prefix='/cart') # Folder cart
app.register_blueprint(bp_transaction, url_prefix='/trabp_transaction') # Folder trabp_transaction

# ===== Buat Tabel =====
db.create_all()

# ===== JWT KEY =====
app.config['JWT_SECRET_KEY'] = 'SFsieaaBsLEpecP675r243faM8oSB2hV'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

jwt = JWTManager(app) 

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return identity
