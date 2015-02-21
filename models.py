#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database import db
import datetime


class User(db.Model):
    login = db.Column(db.String(8), primary_key=True)
    email = db.Column(db.String(100))
    date_join = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    last_login = db.Column(db.DateTime(), default=datetime.datetime.utcnow())

    collections = db.relationship('Collection', backref='user', lazy='dynamic')

    def __init__(self, login):
        self.login = login
        self.email = "%s@etu.utc.fr" % login

    def __repr__(self):
        return '<User %r>' % self.login


class Echange(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user1 = db.Column(db.String(8), db.ForeignKey('user.login'))
    user2 = db.Column(db.String(8), db.ForeignKey('user.login'))
    # User1 donne ecocup1
    ecocup1 = db.Column(db.Integer(), db.ForeignKey('ecocup.id'))
    ecocup2 = db.Column(db.Integer(), db.ForeignKey('ecocup.id'))
    date_execution = db.Column(db.DateTime(), default=None)
    date_conf1 = db.Column(db.DateTime(), default=None)
    date_conf2 = db.Column(db.DateTime(), default=None)
    date_cancelled = db.Column(db.DateTime(), default=None)
    canceller = db.Column(db.String(8), default=None)
    date_creation = db.Column(db.DateTime(), default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Echange %r>' % self.id


class Ecocup(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(50))
    semestre = db.Column(db.String(3))
    asso = db.Column(db.String(50))
    nb_exemplaire = db.Column(db.Integer())
    appreciation = db.Column(db.Integer())
    commentaires = db.Column(db.String(140))

    collections = db.relationship('Collection', backref='ecocup_ref', lazy='dynamic')
    echanges_1 = db.relationship('Echange', backref='ecocup1_ref', foreign_keys=[Echange.ecocup1], lazy='dynamic')
    echanges_2 = db.relationship('Echange', backref='ecocup2_ref', foreign_keys=[Echange.ecocup2], lazy='dynamic')

    def __repr__(self):
        return '<Ecocup %r>' % self.id


class Collection(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    login_user = db.Column(db.String(8), db.ForeignKey('user.login'), index=True)
    ecocup = db.Column(db.Integer(), db.ForeignKey('ecocup.id'), index=True)
    in_collection = db.Column(db.Integer())
    accepte_echange = db.Column(db.Integer())
    souhaite = db.Column(db.Integer())
    date_mise_a_jour = db.Column(db.DateTime(), default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Collection %r %r>' % (self.id, self.nom_ecocup, self.in_collection, self.login_user)


class Like(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(8), db.ForeignKey('user.login'))
    ecocup = db.Column(db.Integer())
    valeur = db.Column(db.Integer())

    def __repr__(self):
        return '<Like %r>' % self.id
