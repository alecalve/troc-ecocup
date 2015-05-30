from flask import render_template, Blueprint, session, flash, request
from helpers import user_required
from models import User
from database import db


bp = Blueprint('profil', __name__, url_prefix='/profil/')


@bp.route('')
@user_required
def me():
    user = User.query.get(session["username"])
    return render_template("profil/index.html", **locals())


@bp.route('email', methods=["POST"])
@user_required
def email():
    user = User.query.get(session["username"])
    user.email = request.form["email"]
    db.session.commit()

    flash("Ton email a été changé", "success")
    return render_template("profil/index.html", **locals())


@bp.route('tel', methods=["POST"])
@user_required
def tel():
    user = User.query.get(session["username"])
    user.tel = request.form["tel"]
    db.session.commit()

    flash("Ton téléphone a été changé", "success    ")
    return render_template("profil/index.html", **locals())


@bp.route('deactivate', methods=["POST"])
@user_required
def deactivate():
    user = User.query.get(session["username"])
    user.active = not user.active
    db.session.commit()
    if user.active:
        flash("Ta collection a été activée !", "success")
    else:
        flash("Ta collection a été désactivée !", "success")

    return render_template("profil/index.html", **locals())
