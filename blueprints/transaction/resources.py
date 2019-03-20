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
from ..barang import *

bp_transaction = Blueprint('transaction', __name__)
api = Api(bp_transaction)


#### book RESOURCE CLASS
#### All Data
class TransResource(Resource):
    @jwt_required
    def get(self, id=None):
        if id == None:
            if get_jwt_claims()['type'] == 'client':
                parser = reqparse.RequestParser()
                parser.add_argument('p', location='args', type=int, default=1)
                parser.add_argument('rp', location='args', type=int, default=5)
                args = parser.parse_args()

                # Rumus (p*rp)-rp
                offset = (args['p'] * args['rp']) - args['rp']
                
                # Memunculkan data semua (ditampilkan sesuai jumlah rp)
                cart_all = Carts.query
                get_all = []
                for get_data in cart_all:#.limit(args['rp']).offset(offset).all():
                    if get_data.user_pembeli == get_jwt_claims()['key']:
                        get_all.append(marshal(get_data, Transactions.response_field))
                return get_all, 200, { 'Content-Type': 'application/json' }
            
        else:
            if get_jwt_claims()['type'] == 'client':
                cart = Transactions.query.get(id)
                if cart is not None and cart.user_pembeli == get_jwt_claims()['key']:
                    return marshal(cart, Transactions.response_field), 200, { 'Content-Type': 'application/json' }
                return {'status': 'NOT_FOUND', 'message': 'Anda belum membeli apapun'}, 404, { 'Content-Type': 'application/json' }

    @jwt_required
    def post(self):
        if get_jwt_claims()['type'] == 'client' or get_jwt_claims()['type'] == 'admin':
            parser = reqparse.RequestParser()
            parser.add_argument('resi', location='json', type=int, required=True)
            parser.add_argument('jumlah', location='json', type=int, required=True)
            args = parser.parse_args()
            
            # Fungsi memanggil tabel barang
            barang = Barangs.query.get(args['resi'])


            # ==========(sentralize)==========
            # Kalkulasi sisa barang
            calc_barang = barang.jumlah - args['jumlah']
            
            if calc_barang < 0:
                return {'status':'NOT_AVAILABLE', 'message':'The quantity stuff that requested is too many'}, 200, { 'Content-Type': 'application/json' }
            if calc_barang > barang.jumlah:
                return {'status':'INVALID', 'message':"Too many stuff that you've input. Please check again"}, 200, { 'Content-Type': 'application/json' }

            barang.barang = barang.barang
            barang.deskripsi = barang.deskripsi
            barang.jenis = barang.jenis
            barang.harga = barang.harga

            # jika sisa 0, maka not available
            if calc_barang == 0:
                barang.status = "Not_Available"
                barang.jumlah = 0
            
            barang.status = barang.status
            barang.jumlah = calc_barang
            db.session.commit()

            # untuk cart
            cart_add = Transactions(None, args['resi'], None, None, None, None, None, None, None)
            cart_add.user_pembeli = get_jwt_claims()['key']
            cart_add.barang = barang.barang
            cart_add.deskripsi = barang.deskripsi
            cart_add.jenis = barang.jenis
            cart_add.harga = barang.harga
            cart_add.status = barang.status
            cart_add.jumlah = args['jumlah']
            db.session.add(cart_add)
            db.session.commit()
            return marshal(cart_add, Transactions.response_field), 200, { 'Content-Type': 'application/json' }
        return {'status': 'USERS_ONLY', 'message': 'Only for users'}, 404, { 'Content-Type': 'application/json' }

    @jwt_required
    def put(self, id=None):
        if get_jwt_claims()['type'] == 'client' or get_jwt_claims()['type'] == 'admin':
            parser = reqparse.RequestParser()
            parser.add_argument('id', location='json', type=int, required=True)
            parser.add_argument('resi', location='json', type=int, required=True)
            parser.add_argument('jumlah_tambah', location='json', type=int, default=0)
            parser.add_argument('jumlah_kurang', location='json', type=int, default=0)
            args = parser.parse_args()
            
            # ambil dari resi json
            barang = Barangs.query.get(args['resi'])
            cart = Transactions.query.get(args['id'])

            if cart.user_pembeli == get_jwt_claims['key']:
                total_barang = barang.jumlah + cart.jumlah

                if args['jumlah_tambah'] == 0:
                    calc_barang = barang.jumlah + args['jumlah_kurang']
                    calc_cart = cart.jumlah - args['jumlah_kurang']

                if args['jumlah_kurang'] == 0:
                    calc_barang = barang.jumlah - args['jumlah_tambah']
                    calc_cart = cart.jumlah + args['jumlah_tambah']
                
                # ==========(sentralize)=========            
                if calc_barang < 0:
                    return {'status':'NOT_AVAILABLE', 'message':'This item is no longer available right now'}, 200, { 'Content-Type': 'application/json' }

                if calc_barang > total_barang:
                    return {'status':'INVALID', 'message':"Too many stuff that you've input. Please check again"}, 200, { 'Content-Type': 'application/json' }

                # Untuk barang
                barang.barang = barang.barang
                barang.deskripsi = barang.deskripsi
                barang.jenis = barang.jenis
                barang.harga = barang.harga

                if barang.status == 'Not_Available' and calc_barang > 0:
                    barang.status = 'Available'
                    
                # jika sisa 0, maka not available
                if calc_barang == 0:
                    barang.status = "Not_Available"
                    barang.jumlah = 0

                barang.status = barang.status
                barang.jumlah = calc_barang
                db.session.commit()

                # untuk cart
                cart.resi = cart.resi
                cart.user_pembeli = cart.user_pembeli
                cart.barang = cart.barang
                cart.deskripsi = cart.deskripsi
                cart.jenis = cart.jenis
                cart.harga = cart.harga
                cart.status = cart.status
                cart.jumlah = calc_cart
                db.session.commit()

            return marshal(cart, Transactions.response_field), 200, { 'Content-Type': 'application/json' }
        return {'status': 'USERS_ONLY', 'message': 'Only for users'}, 404, { 'Content-Type': 'application/json' }

    @jwt_required
    def delete(self, id=None):
        if get_jwt_claims()['type'] == 'client' or get_jwt_claims()['type'] == 'admin':
            parser = reqparse.RequestParser()
            parser.add_argument('id', location='json', type=int, required=True)
            parser.add_argument('resi', location='json', type=int, required=True)
            args = parser.parse_args()

            barang = Barangs.query.get(args['resi'])
            cart = Transactions.query.get(args['id'])

            if cart.user_pembeli == get_jwt_claims()['key']:
                total_barang = barang.jumlah + cart.jumlah

                barang.barang = barang.barang
                barang.deskripsi = barang.deskripsi
                barang.jenis = barang.jenis
                barang.harga = barang.harga
                barang.status = barang.status
                barang.jumlah = total_barang
                db.session.commit()

                db.session.delete(cart)
                db.session.commit()
                return { 'status':'COMPLETE', 'message': 'Delete complete' }, 200, { 'Content-Type': 'application/json' }
            return { 'status':'NOT_FOUND', 'message': 'Stuff in cart not found' }, 200, { 'Content-Type': 'application/json' }
        return {'status': 'USERS_ONLY', 'message': 'Only for users'}, 404, { 'Content-Type': 'application/json' }


api.add_resource(TransResource,'', '/<int:id>')