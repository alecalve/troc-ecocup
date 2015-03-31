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

    username = session["username"]
    collections = Collection.query.filter_by(login_user=session["username"]).all()

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

        if modification["possede"] == 1:
            modification["souhaite"] = 0

        collec = Collection().query.get(id)
        collec.possede = modification["possede"]
        collec.souhaite = modification["souhaite"]
        collec.ngoods = modification["ngoods"]

    db.session.commit()

    return redirect(url_for("echange.compute"))
