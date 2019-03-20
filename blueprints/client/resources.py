import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
# ===== Untuk import db =====
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims

# ===== Untuk import __init__.py =====
from ..users import *

bp_client = Blueprint('client', __name__)
api = Api(bp_client)


#### data RESOURCE CLASS
#### All Data
class ClientResource(Resource):
    # for client see their own ID/ admin for see all ID
    @jwt_required
    def get(self, id=None):
        if id == None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', location='args', type=int, default=1)
            parser.add_argument('rp', location='args', type=int, default=5)
            parser.add_argument('name', location='args')
            args = parser.parse_args()

            # Rumus (p*rp)-rp
            offset = (args['p'] * args['rp']) - args['rp']

            # Memunculkan data semua (ditampilkan sesuai jumlah rp)
            qry_all = Users.query
            get_all = []

            if args['name'] is not None:
                qry_all = qry_all.filter(Users.id.like("%"+args['name']+"%"))

            if get_jwt_claims()['type'] == "admin":
                for get_data in qry_all.limit(args['rp']).offset(offset).all():
                    get_all.append(marshal(get_data, Users.response_field))
                return get_all, 200, {'Content-Type': 'application/json' }
            
            if get_jwt_claims()['type'] == "client":
                qry = Users.query.get(get_jwt_claims()['id'])
                return marshal(qry, Users.response_field), 200, { 'Content-Type': 'application/json' }
            
        else:
            qry = Users.query.get(id)
            if qry is not None:
                if get_jwt_claims()['type'] == "admin":
                    return marshal(qry, Users.response_field), 200, { 'Content-Type': 'application/json' }
                
                if get_jwt_claims()['type'] == "client" and get_jwt_claims()['id'] == id:
                    return marshal(qry, Users.response_field), 200, { 'Content-Type': 'application/json' }
            
            return { 'status': 'NOT_FOUND', 'message': 'User not found. Please try again' }, 404, { 'Content-Type': 'application/json' }
    # make user client
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', location='json', required=True)
        parser.add_argument('secret', location='json', required=True)
        args = parser.parse_args()

        # ==========(sentralize)==========
        client = Users(None, 'client', args['key'], args['secret'], 'active')
        db.session.add(client)
        db.session.commit()
        return marshal(client, Users.response_field), 200, { 'Content-Type': 'application/json' }
    
    # for change password
    @jwt_required
    def put(self, id=None):
        if get_jwt_claims()['type'] == 'client':
            parser = reqparse.RequestParser()
            parser.add_argument('key', location='json', required=True)
            parser.add_argument('secret', location='json', required=True)
            parser.add_argument('new_secret', location='json', required=True)
            args = parser.parse_args()
        
            if get_jwt_claims()['key'] == args['key'] and get_jwt_claims()['secret'] == args['secret']:
                if get_jwt_claims()['status'] != 'active':
                    return { 'status':'DELETED', 'message': 'Already deleted' }, 200, { 'Content-Type': 'application/json' }
                qry = Users.query.get(get_jwt_claims()['id'])
                qry.secret = args['new_secret']
                db.session.commit()
            return { 'status':'COMPLETE', 'message': 'Change password complete' }, 200, { 'Content-Type': 'application/json' }
        return { 'status': 'LOGIN_FIRST', 'message': 'You should login first' }, 404, { 'Content-Type': 'application/json' }

    # for delete client by user/admin
    @jwt_required
    def delete(self, id=None):
        if get_jwt_claims()['type'] == 'client':
            parser = reqparse.RequestParser()
            parser.add_argument('key', location='json', required=True)
            parser.add_argument('secret', location='json', required=True)
            args = parser.parse_args()
        
            if get_jwt_claims()['key'] == args['key'] and get_jwt_claims()['secret'] == args['secret']:
                if get_jwt_claims()['status'] != 'active':
                    return { 'status':'DELETED', 'message': 'Already deleted' }, 200, { 'Content-Type': 'application/json' }
                qry = Users.query.get(get_jwt_claims()['id'])
        
        if get_jwt_claims()['type'] == 'admin':
            parser = reqparse.RequestParser()
            parser.add_argument('id', location='json', type=int)
            args = parser.parse_args()

            if id != None:
                qry = Users.query.get(id)

            if id == None:
                if args['id'] != None:
                    qry = Users.query.get(args['id'])
                if args['id'] == None:
                    return { 'status':'NEED_ID', 'message': 'Fill the ID of user first' }, 200, { 'Content-Type': 'application/json' }        

        if qry != None and qry.status != 'deleted' and get_jwt_claims()['type'] == "client" or get_jwt_claims()['type'] == "admin":
            qry.status = 'deleted'
            db.session.commit()
            return { 'status':'COMPLETE', 'message': 'Delete complete' }, 200, { 'Content-Type': 'application/json' }

        return { 'status': 'LOGIN_FIRST', 'message': 'You should login first' }, 404, { 'Content-Type': 'application/json' }    

api.add_resource(ClientResource,'', '/<int:id>')
