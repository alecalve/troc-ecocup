#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint
import conf
from models import User
from helpers import user_required
import datetime
from database import db

bp = Blueprint('collection', __name__, url_prefix='/collection/')

@bp.route('')
@user_required
def mine():
    """ Affiche la collection de l’utilisateur connecté """
    
    username = session["username"]
    return render_template("collection/index.html", **locals())

@bp.route("add")
def ajout():
    """ Ajoute une collection quand un utilisateur n’en a pas """

    username = session["username"]
    return render_template("collection/add.html", **locals())

@bp.route("logout")
def logout():
    """ Déconnection du CAS """
    
    session["logged_in"] = False
    return redirect("%slogout" % (conf.CAS,))
    


