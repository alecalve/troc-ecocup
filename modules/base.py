#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint
import conf
from helpers import user_required

bp = Blueprint('base', __name__, url_prefix='/')


@bp.route('')
@user_required
def index():
	username = session["username"]
	return render_template("base/index.html", **locals())

