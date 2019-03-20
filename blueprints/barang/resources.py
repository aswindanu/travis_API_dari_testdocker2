import logging, json, random
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
# ===== Untuk import db =====
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints.client import *
from blueprints.auth import *

# ===== Untuk import __init__.py =====
from . import *

bp_barang = Blueprint('barang', __name__)
api = Api(bp_barang)


#### book RESOURCE CLASS
#### All Data
class BarangResource(Resource):
    def get(self, id=None):
        if id == None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', location='args', type=int, default=1)
            parser.add_argument('rp', location='args', type=int, default=5)
            parser.add_argument('barang', location='args')
            parser.add_argument('jenis', location='args')
            args = parser.parse_args()

            # Rumus (p*rp)-rp
            offset = (args['p'] * args['rp']) - args['rp']
            
            # Memunculkan data semua (ditampilkan sesuai jumlah rp)
            barang_all = Barangs.query

            # search dari nama barang
            if args['barang'] is not None:
                barang_all = barang_all.filter(Barangs.barang.like("%"+args['barang']+"%"))
            
            # search dari jenis barang
            if args['jenis'] is not None:
                barang_all = barang_all.filter(Barangs.jenis.like("%"+args['jenis']+"%"))

            get_all = []
            for get_data in barang_all.limit(args['rp']).offset(offset).all():
                get_all.append(marshal(get_data, Barangs.response_field))
            return get_all, 200, { 'Content-Type': 'application/json' }
            
        else:
            barang = Barangs.query.get(id)
            if barang is not None:
                return marshal(barang, Barangs.response_field), 200, { 'Content-Type': 'application/json' }
            return {'status': 'NOT_FOUND', 'message': 'Book not found'}, 404, { 'Content-Type': 'application/json' }

    @jwt_required
    def post(self):
        if get_jwt_claims()['type'] == 'admin':
            parser = reqparse.RequestParser()
            resi = random.randrange(10000, 99999)
            parser.add_argument('barang', location='json', required=True)
            parser.add_argument('deskripsi', location='json', required=True)
            parser.add_argument('jenis', location='json', required=True)
            parser.add_argument('harga', location='json',  type=int)
            parser.add_argument('jumlah', location='json', type=int)
            args = parser.parse_args()
            
            # ==========(sentralize)==========
            barang = Barangs(resi, args['barang'], args['deskripsi'], args['jenis'], args['harga'], 'Available', args['jumlah'])
            db.session.add(barang)
            db.session.commit()
            return marshal(barang, Barangs.response_field), 200, { 'Content-Type': 'application/json' }
        return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }

    @jwt_required
    def put(self, id=None):
        if get_jwt_claims()['type'] == 'admin':
            parser = reqparse.RequestParser()
            parser.add_argument('resi', location='json')
            parser.add_argument('barang', location='json')
            parser.add_argument('deskripsi', location='json')
            parser.add_argument('jenis', location='json')
            parser.add_argument('harga', location='json',  type=int)
            parser.add_argument('status', location='json')
            parser.add_argument('jumlah', location='json')
            args = parser.parse_args()

            # ambil dari resi json
            if id == None:
                barang = Barangs.query.get(args['resi'])
            
            # ambil dari resi (ditulis website)
            if id != None:
                barang = Barangs.query.get(id) 
            
            temp = barang
                # ==========(sentralize)=========
            if barang != None:
                if args['barang'] != None:
                    barang.barang = args['barang']
                if args['deskripsi'] != None:
                    barang.deskripsi = args['deskripsi']
                if args['jenis'] != None:
                    barang.jenis = args['jenis']
                if args['harga'] != None:
                    barang.harga = args['harga']
                if args['status'] != None:
                    barang.status = args['status']
                if args['jumlah'] != None:
                    barang.jumlah = args['jumlah']
                
                if barang.barang == None:
                    barang.barang = temp['barang']
                if barang.deskripsi == None:
                    barang.deskripsi = temp['deskripsi']
                if barang.jenis == None:
                    barang.jenis = temp['jenis']
                if barang.harga == None:
                    barang.harga = temp['harga']
                if barang.status == None:
                    barang.status = temp['status']
                if barang.jumlah == None:
                    barang.jumlah = temp['jumlah']

                db.session.commit()
                return marshal(barang, Barangs.response_field), 200, { 'Content-Type': 'application/json' }
            if barang == None:
                return { 'status': 'NOT_FOUND', 'message': 'Stuff not found' }, 404, { 'Content-Type': 'application/json' }                
        return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }

    @jwt_required
    def delete(self, id=None):
        if get_jwt_claims()['type'] == 'admin':
            parser = reqparse.RequestParser()
            parser.add_argument('resi', location='json', type=int)
            args = parser.parse_args()
        
            if id != None:
                barang = Barangs.query.get(id)

            if id == None:
                barang = Barangs.query.get(args['resi'])

            if barang != None:
                db.session.delete(barang)
                db.session.commit()
                return { 'status':'COMPLETE', 'message': 'Delete complete' }, 200, { 'Content-Type': 'application/json' }
            return { 'status': 'NOT_FOUND', 'message': 'Stuff not found' }, 404, { 'Content-Type': 'application/json' }
        return { 'status': 'ADMIN_ONLY', 'message': 'Only allowed for admin' }, 404, { 'Content-Type': 'application/json' }

api.add_resource(BarangResource,'', '/<int:id>')