#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint
import conf
from helpers import user_required
from models import Echange, User, Collection
from database import db
import datetime
from sqlalchemy import or_

bp = Blueprint('echange', __name__, url_prefix='/echange/')

def rewrite_echanges(echanges):
  e = []
  print "dans la fonction", echanges
  for echange in echanges:
    print echange
    print len(echanges)
    other = echange.user1 if echange.user1 != session["username"] else echange.user2
    other = User.query.get(other)
    i = 1 if session["username"] == echange.user1 else 2
    donne = echange.ecocup1_ref.nom if i == 1 else echange.ecocup2_ref.nom
    recu = echange.ecocup2_ref.nom if i == 1 else echange.ecocup1_ref.nom
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

  r_echanges_en_cours = Echange.query.filter(or_(Echange.user1 == username, Echange.user2 == username)).filter_by(date_cancelled=None, date_execution=None).all()
  print "requete", r_echanges_en_cours
  echanges_en_cours = rewrite_echanges(r_echanges_en_cours) if r_echanges_en_cours else None

  r_echanges_termines = Echange.query.filter(Echange.date_execution!=None, or_(Echange.user2==username, Echange.user1==username)).all()
  echanges_termines = rewrite_echanges(r_echanges_termines) if r_echanges_termines else None
  
  r_echanges_annules = Echange.query.filter(Echange.date_cancelled!=None, or_(Echange.user2==username, Echange.user1==username)).all()
  echanges_annules = rewrite_echanges(r_echanges_annules) if r_echanges_annules else None
  
  return render_template("echange/index.html", **locals())

@bp.route("compute")
@user_required
def compute():
  username = session["username"]
  requete = """
SELECT c1.login_user AS u1, c2.login_user AS u2, c1.ecocup AS e1
FROM `collection` c1, collection c2
WHERE (
c1.login_user = "%s"
OR c2.login_user = "%s"
)
AND c1.ecocup = c2.ecocup
AND c1.souhaite = 1
AND c2.accepte_echange =1;
""" % (username, username,)

  matches = db.engine.execute(requete)
  matches = list(matches)

  if len(matches) < 2:
    return redirect(url_for("collection.mine"))
    
  real_matchs = []
  print matches
  for match1 in matches:
    correspondant = [m for m in matches if m[1] == match1[0]]
    if len(correspondant) == 0:
      break
    correspondant = correspondant[0]
    real_matchs.append([match1[0], correspondant[2], match1[1], match1[2]])
    matches.remove(correspondant)
    matches.remove(match1)

  print real_matchs
  for match in real_matchs:
    echange = Echange(user1=match[0], ecocup1=match[1], user2=match[2], ecocup2=match[3])

    #Écocup que donne user1 (match[1])
    ecocup1 = Collection.query.filter_by(login_user=match[0], ecocup=match[1]).first()
    #Écocup que reçoit user1 (match[3])
    ecocup12 = Collection.query.filter_by(login_user=match[0], ecocup=match[3]).first()
        
    ecocup1.in_collection = 0
    ecocup1.souhaite = 0
    ecocup1.accepte_echange = 0
        
    ecocup12.in_collection = 1
    ecocup12.souhaite = 0
    ecocup12.accepte_echange = 0

    #Écocup que donne user2 (match[3])
    ecocup2 = Collection.query.filter_by(login_user=match[2], ecocup=match[3]).first()
    #Écocup que reçoit user2 (match[3])
    ecocup21 = Collection.query.filter_by(login_user=match[2], ecocup=match[1]).first()
        
    ecocup2.in_collection = 0
    ecocup2.souhaite = 0
    ecocup2.accepte_echange = 0
        
    ecocup21.in_collection = 1
    ecocup21.souhaite = 0
    ecocup21.accepte_echange = 0

    #On trouve la personne à qui on envoie le mail
    other = match[0] if match[0] != username else match[2]
    ecocup_connected = match[1] if match[0] == username else match[3]
    ecocup_non_connected = match[1] if ecocup_connected == match[3] else match[3]
        
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

  echange = Echange.query.get(id)
  
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

  echange = Echange.query.get(id)
  
  echange.date_cancelled = datetime.datetime.utcnow()
  echange.canceller = username

  if echange.date_conf1 is not None and echange.conf2 is not None:
    echange.date_execution = datetime.datetime.utcnow()

  ecocup1 = Collection.query.filter_by(login_user=echange.user1, ecocup=echange.ecocup1).first()
  ecocup12 = Collection.query.filter_by(login_user=echange.user1, ecocup=echange.ecocup2).first()
  ecocup2 = Collection.query.filter_by(login_user=echange.user2, ecocup=echange.ecocup2).first()
  ecocup21 = Collection.query.filter_by(login_user=echange.user2, ecocup=echange.ecocup1).first()

  ecocup1.in_collection = 1
  ecocup1.souhaite = 0
  ecocup1.accepte_echange = 0
        
  ecocup12.in_collection = 0
  ecocup12.souhaite = 1
  ecocup12.accepte_echange = 0
     
  ecocup2.in_collection = 1
  ecocup2.souhaite = 0
  ecocup2.accepte_echange = 0
       
  ecocup21.in_collection = 0
  ecocup21.souhaite = 1
  ecocup21.accepte_echange = 0

  db.session.commit()
  flash("Échange annulé", "danger")
  
  return redirect(url_for("echange.compute"))

