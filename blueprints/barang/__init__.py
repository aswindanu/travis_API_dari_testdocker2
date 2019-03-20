import random, logging
from blueprints import db
from flask_restful import fields

class Barangs(db.Model):

    __tablename__ = "barang"
    resi = db.Column(db.Integer, primary_key=True, unique=True)
    barang = db.Column(db.String(50))
    deskripsi = db.Column(db.String(200))
    jenis = db.Column(db.String(50))
    harga = db.Column(db.Integer)
    status = db.Column(db.String(50))
    jumlah = db.Column(db.Integer)

    # ===== Respon Field =====
    response_field = {
        'resi' : fields.Integer,
        'barang' : fields.String,
        'deskripsi' : fields.String,
        'jenis' : fields.String,
        'harga' : fields.Integer,
        'status' : fields.String,
        'jumlah' : fields.Integer
    }
    
    def __init__(self, resi, barang, deskripsi, jenis, harga, status, jumlah):
        self.resi = resi
        self.barang = barang
        self.deskripsi = deskripsi
        self.jenis = jenis
        self.harga = harga
        self.status = status
        self.jumlah = jumlah

    def __repr__(self):
        return '<Barang %r>' % self.resi
