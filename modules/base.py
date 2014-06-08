#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint, jsonify
import conf
from helpers import user_required
from database import db
from models import Ecocup, Echange, Like

bp = Blueprint('base', __name__, url_prefix='/')


@bp.route('')
@user_required
def index():
  username = session["username"]
  last_echanges = Echange.query.filter(Echange.date_execution!=None).order_by(Echange.date_execution).limit(10)
  ecocups = list(enumerate(Ecocup.query.all()))
  return render_template("base/index.html", **locals())

@bp.route('like/<int:ecocup>')
@user_required
def like(ecocup):
  username = session["username"]
  like = Like.query.filter_by(user=username, ecocup=ecocup).first()
  print like
  if like is None:
    like = Like(user=username, ecocup=ecocup, valeur=1)
    db.session.add(like)
  else:
    like.valeur = 1

  ecocup = Ecocup.query.get(ecocup)
  if ecocup is None:
    return jsonify({"error": True})
  db.session.commit()
  ecocup.appreciation = sum(map(lambda l: l.valeur, Like.query.filter_by(ecocup=ecocup.id).all()))
  db.session.commit()
  return jsonify({"appreciation" :ecocup.appreciation, "error": False})

@bp.route('dislike/<int:ecocup>')
@user_required
def dislike(ecocup):
  username = session["username"]
  like = Like.query.filter_by(user=username, ecocup=ecocup).first()

  if like is None:
    like = Like(user=username, ecocup=ecocup, valeur=-1)
    db.session.add(like)
  else:
    like.valeur = -1

  ecocup = Ecocup.query.get(ecocup)
  if ecocup is None:
    return jsonify({"error": True})
  db.session.commit()
  ecocup.appreciation = sum(map(lambda l: l.valeur, Like.query.filter_by(ecocup=ecocup.id).all()))
  db.session.commit()
  return jsonify({"appreciation": ecocup.appreciation, "error": False})
