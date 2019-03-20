import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
# ===== Untuk import db =====
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims

# ===== Untuk import __init__.py =====
from ..users import *

bp_admin = Blueprint('admin', __name__)
api = Api(bp_admin)


#### admin RESOURCE CLASS
#### All Data
class AdminResource(Resource):
    # For get all users by ADMIN only
    # @jwt_required
    # def get(self, id=None):
    #     if id == None:
    #         parser = reqparse.RequestParser()
    #         parser.add_argument('p', location='args', type=int, default=1)
    #         parser.add_argument('rp', location='args', type=int, default=5)
    #         parser.add_argument('name', location='json')
    #         args = parser.parse_args()

    #         # Rumus (p*rp)-rp
    #         offset = (args['p'] * args['rp']) - args['rp']

    #         # Memunculkan data semua (ditampilkan sesuai jumlah rp)
    #         qry_all = Users.query
    #         get_all = []

    #         if args['name'] is not None:
    #             qry_all = qry_all.filter(Users.id.like("%"+args['name']+"%"))

    #         if get_jwt_claims()['type'] == "admin":
    #             for get_data in qry_all.limit(args['rp']).offset(offset).all():
    #                 get_all.append(marshal(get_data, Users.response_field))
    #             return get_all, 200, {'Content-Type': 'application/json' }

    #         if get_jwt_claims()['type'] == "client":
    #             return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }
        
    #     else: 
    #         qry = Users.query.get(id)
    #         if qry is not None:

    #             if get_jwt_claims()['type'] == "admin":
    #                 return marshal(qry, Users.response_field), 200, { 'Content-Type': 'application/json' }
                
    #             if get_jwt_claims()['type'] == "client":
    #                 return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }

    #         return { 'status': 'NOT_FOUND', 'message': 'User not found. Please try again' }, 404, { 'Content-Type': 'application/json' }
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
                return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }
            
        else:
            qry = Users.query.get(id)
            if qry is not None:
                if get_jwt_claims()['type'] == "admin":
                    return marshal(qry, Users.response_field), 200, { 'Content-Type': 'application/json' }
                
                if get_jwt_claims()['type'] == "client":
                    return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }
            
            return { 'status': 'NOT_FOUND', 'message': 'User not found. Please try again' }, 404, { 'Content-Type': 'application/json' }

    # for make ID admin
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', location='json', required=True)
        parser.add_argument('secret', location='json', required=True)
        parser.add_argument('code_admin', location='json', required=True)
        args = parser.parse_args()

        # ==========(sentralize)==========
        if args['code_admin'] == 'warcr4ft':
            admin = Users(None, 'admin', args['key'], args['secret'], 'active')
            db.session.add(admin)
            db.session.commit()
            return marshal(admin, Users.response_field), 200, { 'Content-Type': 'application/json' }
        return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }

    # for reactivate user client/admin
    @jwt_required
    def put(self, id=None):
        if get_jwt_claims()['type'] == "admin":
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

            if qry == None:
                return { 'status': 'NOT_FOUND', 'message': 'ID not found' }, 404, { 'Content-Type': 'application/json' } 
            if qry != None and qry.status != 'active':
                qry.status = 'active'
                db.session.commit()
                return { 'status':'COMPLETE', 'message': 'Reactivate complete' }, 200, { 'Content-Type': 'application/json' }

        return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }

    # for delete by ADMIN only
    @jwt_required
    def delete(self, id=None):
        if get_jwt_claims()['type'] == "admin":
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

            if qry == None:
                return { 'status': 'NOT_FOUND', 'message': 'ID not found' }, 404, { 'Content-Type': 'application/json' } 
            if qry != None and qry.status != 'deleted':
                qry.status = 'deleted'
                db.session.commit()
                return { 'status':'COMPLETE', 'message': 'Delete complete' }, 200, { 'Content-Type': 'application/json' }

        return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }

api.add_resource(AdminResource,'', '/<int:id>')
