#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint
from models import User, Collection
from helpers import user_required
from database import db
import json

bp = Blueprint('collection', __name__, url_prefix='/collection/')


@bp.route('')
@user_required
def mine():
    """ Affiche la collection de l’utilisateur connecté """

    collections = User.query.get(session["username"]).collections

    return render_template("collection/index.html", **locals())


@bp.route('update', methods=["POST"])
@user_required
def update():
    """ Met à jour la collection de l’utilisateur connecté """

    text = request.form["json"]
    data = json.loads(text)
    for id, modifs in data.items():
        if modifs["wishesit"] == 1:
            modifs["hasit"] = 0

        if modifs["hasit"] == 1:
            modifs["wishesit"] = 0

        collec = Collection.query.get(id)
        collec.has_it = modifs["hasit"]
        collec.wishes_it = modifs["wishesit"]
        collec.value = modifs["value"]

        db.session.commit()

    return redirect(url_for("exchange.compute"))
