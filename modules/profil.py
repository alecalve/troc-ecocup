#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, session, Blueprint
from helpers import user_required

bp = Blueprint('profil', __name__, url_prefix='/profil/')


@bp.route('')
@user_required
def me():
    username = session["username"]
    return render_template("profil/index.html", **locals())
