#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, url_for, redirect, request, session, flash, Blueprint
import conf
import requests
from xml.dom.minidom import parseString

bp = Blueprint('cas', __name__, url_prefix='/cas/')

@bp.route('login')
def login():
    """ Loggue un utilisateur sur le cas """
     
    if session.has_key('logged_in') and session["logged_in"]:
        return redirect(url_for("base.index"))

    if not request.args.get('ticket'):
        return redirect("%slogin?service=%s" % (conf.CAS, conf.HOSTNAME + url_for('cas.authenticate')))

@bp.route("authenticate")
def authenticate():
	if not request.args.get('ticket'):
		return redirect(url_for("base.index"))

	ticket = request.args.get("ticket")
	r = requests.get("%sserviceValidate?ticket=%s&service=%s" % (conf.CAS, ticket, conf.HOSTNAME + url_for('cas.authenticate')))
	
	if "authenticationFailure" in r.text:
	    return redirect(url_for("base.index"))
	else:
	    dom = parseString(r.text)
	    session["username"] = dom.getElementsByTagName("cas:user")[0].firstChild.nodeValue
	    session["logged_in"] = True
	    flash("Bienvenue !", "success")
	    return redirect(url_for("base.index"))

@bp.route("logout")
def logout():
    """ Déconnection du CAS """
    
    session["logged_in"] = False
    return redirect("%slogout" % (conf.CAS,))
    

