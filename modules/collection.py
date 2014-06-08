#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint
import conf
from models import User, Ecocup, Collection, Echange
from helpers import user_required
import datetime
from sqlalchemy.orm import join
from database import db
import json

bp = Blueprint('collection', __name__, url_prefix='/collection/')

@bp.route('')
@user_required
def mine():
    """ Affiche la collection de l’utilisateur connecté """

    username = session["username"]

    collections = Collection.query.filter_by(login_user=session["username"])

    return render_template("collection/index.html", **locals())

@bp.route('update', methods=["POST"])
@user_required
def update():
    """ Met à jour la collection de l’utilisateur connecté """

    text = request.form["json"]
    data = json.loads(text)
    for id, modifs in data.items():
        modification = {}
        for modif in modifs:
            modification[modif["type"]] = modif["value"]
        if modification["collection"] == 1:
            modification["souhaite"] = 0
        else:
            modification["echange"] = 0

        collec = Collection().query.get(id)
        collec.in_collection = modification["collection"]
        collec.souhaite = modification["souhaite"]
        collec.accepte_echange = modification["echange"]
        
        db.session.commit()
    return redirect(url_for("echange.compute"))

@bp.route("compare/<string:usr>")
@user_required
def compare(usr):
    username = session["username"]

    if usr == username:
        flash(u"Ça sert à rien de se comparer avec soi-même …", "info")
        return redirect(url_for("collection.mine"))
        
    user = User.query.get(usr)
    
    if user is None:
        flash(u"L’utilisateur saisi n’existe pas", "danger")
        return redirect(url_for("collection.mine"))
        
    collection_connected = Collection.query.filter_by(login_user=username).all()
    collection_other = Collection.query.filter_by(login_user=usr).all()

    collections = zip(collection_connected, collection_other)

    collections = [(c, o) for c, o in collections if c.in_collection != o.in_collection ]
    
    return render_template("collection/compare.html", **locals())
