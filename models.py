#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database import db
import datetime

class User(db.Model):
    login = db.Column(db.String(8), primary_key=True)
    date_join = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    last_login = db.Column(db.DateTime(),default=datetime.datetime.utcnow())

    def __init__(self, login):
        self.login = login
        
    def __repr__(self):
        return '<User %r>' % self.login
