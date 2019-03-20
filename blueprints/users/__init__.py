import random, logging
from blueprints import db
import logging, json
from flask import Blueprint
from flask_restful import Resource, Api, reqparse, abort, marshal,fields

class Users(db.Model):

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50))
    key = db.Column(db.String(50), unique=True)
    secret = db.Column(db.String(50))
    status = db.Column(db.String(50))

    # ===== Respon Field =====
    response_field = {
        'id' : fields.Integer,
        'type' : fields.String,
        'key' : fields.String,
        'secret' : fields.String,
        'status' : fields.String
    }
    
    def __init__(self, id, type, key, secret, status):
        self.id = id
        self.type = type
        self.key = key
        self.secret = secret
        self.status = status

    def __repr__(self):
        return '<User %r>' % self.id