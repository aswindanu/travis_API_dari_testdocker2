import random, logging
from blueprints import db
from flask_restful import fields
from ..barang import *

class Carts(db.Model):
    barang = Barangs

    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resi = db.Column(db.Integer)
    user_pembeli = db.Column(db.String(50)) 
    barang = db.Column(db.String(50))
    deskripsi = db.Column(db.String(200))
    jenis = db.Column(db.String(50))
    harga = db.Column(db.Integer)
    status = db.Column(db.String(50))
    jumlah = db.Column(db.Integer)

    # ===== Respon Field =====
    response_field = {
        'id': fields.Integer,
        'resi' : fields.Integer,
        'user_pembeli' : fields.String,
        'barang' : fields.String,
        'deskripsi' : fields.String,
        'jenis' : fields.String,
        'harga' : fields.Integer,
        'status' : fields.String,
        'jumlah' : fields.Integer
    }
    
    def __init__(self, id, resi, user_pembeli, barang, deskripsi, jenis, harga, status, jumlah):
        self.id = id
        self.resi = resi
        self.user_pembeli = user_pembeli
        self.barang = barang
        self.deskripsi = deskripsi
        self.jenis = jenis
        self.harga = harga
        self.status = status
        self.jumlah = jumlah

    def __repr__(self):
        return '<Cart %r>' % self.id
