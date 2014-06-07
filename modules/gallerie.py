#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint
import conf
from helpers import user_required

bp = Blueprint('gallerie', __name__, url_prefix='/gallerie/')

@bp.route("ecocups")
@user_required
def ecocups():
    """ Gallerie des écocups """

    username = session["username"]
    return render_template("gallerie/ecocups.html", **locals())
    
@bp.route("achievements")
@user_required
def achievements():
    """ Gallerie des achievements """

    username = session["username"]
    return render_template("gallerie/achievements.html", **locals())

@bp.route("stats")
@user_required
def stats():
    """ Statistiques """

    username = session["username"]
    return render_template("gallerie/stats.html", **locals())
