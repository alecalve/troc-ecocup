from flask import url_for, redirect, request, session, flash, Blueprint
import conf
import requests
from xml.dom.minidom import parseString
from models import User
import datetime
from database import db

bp = Blueprint('cas', __name__, url_prefix='/cas/')


@bp.route('login')
def login():
    """ Loggue un utilisateur sur le cas """

    if 'logged_in' in session and session["logged_in"]:
        return redirect(url_for("base.index"))

    if not request.args.get('ticket'):
        return redirect("%slogin?service=%s" % (conf.CAS, conf.HOSTNAME + url_for('cas.authenticate')))


@bp.route("authenticate")
def authenticate():
    if not request.args.get('ticket'):
        return redirect(url_for("base.index"))

    ticket = request.args.get("ticket")
    r = requests.get(
        "%sserviceValidate?ticket=%s&service=%s" % (conf.CAS, ticket, conf.HOSTNAME + url_for('cas.authenticate')))

    if "authenticationFailure" in r.text:
        return redirect(url_for("base.index"))
    else:
        dom = parseString(r.text)
        username = dom.getElementsByTagName("cas:user")[0].firstChild.nodeValue
        session["username"] = username
        existing = User.query.get(username)
        if existing is None:
            user = User(username)
            if username == "alecalve":
                user.is_admin = 1
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("collection.mine"))
        else:
            existing.last_login = datetime.datetime.now()

        db.session.commit()
        session["logged_in"] = True
        flash("Bienvenue !", "success")
        return redirect(url_for("base.index"))


@bp.route("logout")
def logout():
    """ Déconnection du CAS """

    session["logged_in"] = False
    return redirect("%slogout" % (conf.CAS,))
