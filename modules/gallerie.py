#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint
import conf

bp = Blueprint('gallerie', __name__, url_prefix='/gallerie/')

@bp.route("ecocups")
def ecocups():
    """ Gallerie des écocups """

		username = session["username"]
    return render_template("gallerie/ecocups.html")
    
@bp.route("achievements")
def ecocups():
    """ Gallerie des achievements """

		username = session["username"]
    return render_template("gallerie/achievements.html")

@bp.route("stats")
def ecocups():
    """ Statistiques """

		username = session["username"]
    return render_template("gallerie/stats.html")
