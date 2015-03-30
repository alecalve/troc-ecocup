#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, session, flash, Blueprint
from helpers import user_required
from models import Exchange, User, Collection
from database import db
import datetime
from sqlalchemy import or_

bp = Blueprint('echange', __name__, url_prefix='/echange/')


def rewrite_echanges(echanges):
    e = []
    for echange in echanges:
        other = echange.user1 if echange.user1 != session[
            "username"] else echange.user2
        other = User.query.get(other)
        i = 1 if session["username"] == echange.user1 else 2
        donne = echange.good1_ref.nom if i == 1 else echange.good2_ref.nom
        recu = echange.good2_ref.nom if i == 1 else echange.good1_ref.nom
        confirm = echange.date_conf1 if i == 1 else echange.date_conf2
        e.append({
            "date_creation": echange.date_creation,
            "date_execution": echange.date_execution,
            "date_cancelled": echange.date_cancelled,
            "date_confirmation": confirm,
            "canceller": echange.canceller,
            "id": echange.id,
            "other": other,
            "donne": donne,
            "recu": recu,
            "subject": u"Je veux échanger ta '%s' contre ma '%s'" % (donne, recu)
        })
    return e


@bp.route('')
@user_required
def echanges():
    username = session["username"]

    r_echanges_en_cours = Exchange.query.filter(or_(Exchange.user1 == username, Exchange.user2 == username)).filter_by(
        date_cancelled=None, date_execution=None).all()

    echanges_en_cours = rewrite_echanges(
        r_echanges_en_cours) if r_echanges_en_cours else None

    r_echanges_termines = Exchange.query.filter(Exchange.date_execution is not None, or_(
        Exchange.user2 == username, Exchange.user1 == username)).all()
    echanges_termines = rewrite_echanges(
        r_echanges_termines) if r_echanges_termines else None

    r_echanges_annules = Exchange.query.filter(Exchange.date_cancelled is not None, or_(
        Exchange.user2 == username, Exchange.user1 == username)).all()
    echanges_annules = rewrite_echanges(
        r_echanges_annules) if r_echanges_annules else None

    return render_template("echange/index.html", **locals())


@bp.route("compute")
@user_required
def compute():
    username = session["username"]
    requete = """
SELECT c1.login_user AS u1, c2.login_user AS u2, c1.good AS e1
FROM `collection` c1, collection c2
WHERE (
c1.login_user = "%s"
OR c2.login_user = "%s"
)
AND c1.good = c2.good
AND c1.souhaite = 1
AND c2.accepte_echange =1;
""" % (username, username,)

    matches = db.engine.execute(requete)
    matches = list(matches)

    if len(matches) < 2:
        return redirect(url_for("collection.mine"))

    real_matchs = []
    for match1 in matches:
        correspondant = [m for m in matches if m[1] == match1[0]]
        if len(correspondant) == 0:
            break
        correspondant = correspondant[0]
        real_matchs.append([match1[0], correspondant[2], match1[1], match1[2]])
        matches.remove(correspondant)
        matches.remove(match1)

    for match in real_matchs:
        echange = Exchange(
            user1=match[0], good1=match[1], user2=match[2], good2=match[3])

        # Écocup que donne user1 (match[1])
        good1 = Collection.query.filter_by(
            login_user=match[0], good=match[1]).first()
        # Écocup que reçoit user1 (match[3])
        good12 = Collection.query.filter_by(
            login_user=match[0], good=match[3]).first()

        good1.in_collection = 0
        good1.souhaite = 0
        good1.accepte_echange = 0

        good12.in_collection = 1
        good12.souhaite = 0
        good12.accepte_echange = 0

        # Écocup que donne user2 (match[3])
        good2 = Collection.query.filter_by(
            login_user=match[2], good=match[3]).first()
        # Écocup que reçoit user2 (match[3])
        good21 = Collection.query.filter_by(
            login_user=match[2], good=match[1]).first()

        good2.in_collection = 0
        good2.souhaite = 0
        good2.accepte_echange = 0

        good21.in_collection = 1
        good21.souhaite = 0
        good21.accepte_echange = 0

        # On trouve la personne à qui on envoie le mail
        other = match[0] if match[0] != username else match[2]
        good_connected = match[1] if match[0] == username else match[3]
        good_non_connected = match[
            1] if good_connected == match[3] else match[3]

        user = User.query.get(other)
        connected = User.query.get(username)

        db.session.add(echange)
        db.session.commit()
    if len(real_matchs):
        return redirect(url_for("echange.echanges"))

    return redirect(url_for("collection.mine"))


@bp.route('confirm/<int:id>')
@user_required
def confirm(id):
    username = session["username"]

    echange = Exchange.query.get(id)

    if username == echange.user1:
        echange.date_conf1 = datetime.datetime.utcnow()
    else:
        echange.date_conf2 = datetime.datetime.utcnow()

    if echange.date_conf1 is not None and echange.date_conf2 is not None:
        flash("Échange confirmé !", "success")
        echange.date_execution = datetime.datetime.utcnow()

    db.session.commit()

    return redirect(url_for("echange.echanges"))


@bp.route('cancel/<int:id>')
@user_required
def cancel(id):
    username = session["username"]

    echange = Exchange.query.get(id)

    echange.date_cancelled = datetime.datetime.utcnow()
    echange.canceller = username

    if echange.date_conf1 is not None and echange.date_conf2 is not None:
        echange.date_execution = datetime.datetime.utcnow()

    good1 = Collection.query.filter_by(
        login_user=echange.user1, good=echange.good1).first()
    good12 = Collection.query.filter_by(
        login_user=echange.user1, good=echange.good2).first()
    good2 = Collection.query.filter_by(
        login_user=echange.user2, good=echange.good2).first()
    good21 = Collection.query.filter_by(
        login_user=echange.user2, good=echange.good1).first()

    good1.in_collection = 1
    good1.souhaite = 0
    good1.accepte_echange = 0

    good12.in_collection = 0
    good12.souhaite = 1
    good12.accepte_echange = 0

    good2.in_collection = 1
    good2.souhaite = 0
    good2.accepte_echange = 0

    good21.in_collection = 0
    good21.souhaite = 1
    good21.accepte_echange = 0

    db.session.commit()
    flash("Échange annulé", "danger")

    return redirect(url_for("echange.compute"))
