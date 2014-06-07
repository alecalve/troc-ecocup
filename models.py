#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database import db
import datetime

class User(db.Model):
    login = db.Column(db.String(8), primary_key=True)
    date_join = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    last_login = db.Column(db.DateTime(),default=datetime.datetime.utcnow())
    
    collections = db.relationship('Collection', backref='user', lazy='dynamic')
        
    def __repr__(self):
        return '<User %r>' % self.login

class Ecocup(db.Model):
    nom = db.Column(db.String(50), primary_key=True)
    semestre = db.Column(db.String(3))
    asso = db.Column(db.String(50))
    nb_exemplaire = db.Column(db.Integer())
    appreciation = db.Column(db.Integer())
    
    collections = db.relationship('Collection', backref='nom_ecocup', lazy='dynamic')
        
    def __repr__(self):
        return '<Ecocup %r>' % self.nom
        
class Collection(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(8), db.ForeignKey('user.login'), index=True)
    nom_ecocup = db.Column(db.String(8), db.ForeignKey('ecocup.nom'), index=True)
    in_collection = db.Column(db.Integer())
    accepte_echange = db.Column(db.Integer())
    souhaite = db.Column(db.Integer())
    date_mise_a_jour = db.Column(db.DateTime(),default=datetime.datetime.utcnow())
        
    def __repr__(self):
        return '<Collection %r>' % self.id
        
class Echange(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user1 = db.Column(db.String(8), db.ForeignKey('user.login'))
    user2 = db.Column(db.String(8), db.ForeignKey('user.login'))
    nom_ecocup1 = db.Column(db.String(8), db.ForeignKey('ecocup.nom'))
    nom_ecocup2 = db.Column(db.String(8), db.ForeignKey('ecocup.nom'))
    date = db.Column(db.DateTime(),default=datetime.datetime.utcnow())
        
    def __repr__(self):
        return '<Echange %r>' % self.id

