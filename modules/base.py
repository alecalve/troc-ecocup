#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, session, Blueprint, jsonify
from helpers import user_required
from database import db
from models import Good, Exchange, Like

bp = Blueprint('base', __name__, url_prefix='/')


@bp.route('')
@user_required
def index():
    username = session["username"]
    last_exchanges = Exchange.query.filter(
        Exchange.date_execution is not None).order_by(Exchange.date_execution).limit(10)
    last_exchanges = list(last_exchanges)
    goods = list(enumerate(Good.query.all()))
    return render_template("base/index.html", **locals())


@bp.route('comment-ca-marche')
@user_required
def comment_ca_marche():
    return render_template('base/comment.html')


@bp.route('like/<int:good>')
@user_required
def like(good, value=1):
    username = session["username"]
    like = Like.query.filter_by(user=username, good=good).first()

    if like is None:
        like = Like(user=username, good=good, valeur=1)
        db.session.add(like)
    else:
        like.valeur = 1

    good = Good.query.get(good)
    if good is None:
        return jsonify({"error": True})
    db.session.commit()
    good.appreciation = sum(
        map(lambda l: l.valeur, Like.query.filter_by(good=good.id).all()))
    db.session.commit()
    return jsonify({"appreciation": good.appreciation, "error": False})


@bp.route('dislike/<int:good>')
@user_required
def dislike(good):
    return like(good, value=-1)
