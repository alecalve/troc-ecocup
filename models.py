#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database import db
import datetime


class User(db.Model):
    login = db.Column(db.String(8), primary_key=True)
    email = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean(), default=False)
    date_join = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    last_login = db.Column(db.DateTime(), default=datetime.datetime.utcnow())

    collections = db.relationship('Collection', backref='user', lazy='dynamic')

    def __init__(self, login):
        self.login = login
        self.email = "%s@etu.utc.fr" % login

    def __repr__(self):
        return '<User %r>' % self.login


class Exchange(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user1 = db.Column(db.String(8), db.ForeignKey('user.login'))
    user2 = db.Column(db.String(8), db.ForeignKey('user.login'))
    # User1 donne good1
    good1 = db.Column(db.Integer(), db.ForeignKey('good.id'))
    good2 = db.Column(db.Integer(), db.ForeignKey('good.id'))
    date_execution = db.Column(db.DateTime(), default=None)
    date_conf1 = db.Column(db.DateTime(), default=None)
    date_conf2 = db.Column(db.DateTime(), default=None)
    date_cancelled = db.Column(db.DateTime(), default=None)
    canceller = db.Column(db.String(8), default=None)
    date_creation = db.Column(db.DateTime(), default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Echange %r>' % self.id


class Good(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(50))
    semestre = db.Column(db.String(3))
    asso = db.Column(db.String(50))
    nb_exemplaires = db.Column(db.Integer())
    contenance = db.Column(db.Integer())
    appreciation = db.Column(db.Integer(), default=0)
    commentaires = db.Column(db.String(140))

    collections = db.relationship('Collection', backref='good_ref', lazy='dynamic')
    exchanges_1 = db.relationship('Exchange', backref='good1_ref', foreign_keys=[Exchange.good1], lazy='dynamic')
    exchanges_2 = db.relationship('Exchange', backref='good2_ref', foreign_keys=[Exchange.good2], lazy='dynamic')

    def __repr__(self):
        return '<Good %r>' % self.id


class Collection(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    login_user = db.Column(db.String(8), db.ForeignKey('user.login'), index=True)
    good = db.Column(db.Integer(), db.ForeignKey('good.id'), index=True)
    in_collection = db.Column(db.Integer(), default=0)
    accepte_echange = db.Column(db.Integer(), default=0)
    souhaite = db.Column(db.Integer(), default=1)
    date_mise_a_jour = db.Column(db.DateTime(), default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Collection %r>' % self.id


class Like(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(8), db.ForeignKey('user.login'))
    good = db.Column(db.Integer())
    valeur = db.Column(db.Integer())

    def __repr__(self):
        return '<Like %r>' % self.id
