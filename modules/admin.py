from flask import render_template, session, Blueprint, abort, request, flash
from models import User, Good, Collection
from helpers import user_required
from database import db


bp = Blueprint('admin', __name__, url_prefix='/admin/')


def is_admin_connected():
    user = User.query.get(session["username"])
    return user.is_admin


@bp.route('')
@user_required
def index():
    if not is_admin_connected():
        abort(401)

    ecocups = Good.query.all()

    return render_template("admin/index.html", **locals())


@bp.route('ecocup/add', methods=["POST"])
@user_required
def add():
    if not is_admin_connected():
        abort(401)

    good = Good()
    good.nom = request.form["name"]
    good.asso= request.form["asso"]
    good.semestre = request.form["semestre"]
    good.nb_exemplaires = request.form["exemplaires"]
    good.contenance = request.form["capacity"]
    good.commentaires = request.form["comment"]

    db.session.add(good)

    users = User.query.all()
    for user in users:
       element = Collection(login_user=user.login, good=good.id)
       db.session.add(element)

    db.session.commit()

    flash("Écocup %s ajoutée" % good.nom, "success")

    return render_template("admin/index.html", **locals())


@bp.route('ecocup/edit', methods=["POST"])
@user_required
def edit():
    if not is_admin_connected():
        abort(401)

    ecocup = Good.query.get(request.form["ecocup"])

    return render_template("admin/edit.html", **locals())


@bp.route('ecocup/delete', methods=["POST"])
@user_required
def delete():
    if not is_admin_connected():
        abort(401)

    ecocup = Good.query.get(request.form["ecocup"])
    db.session.delete(ecocup)
    db.session.commit()

    return render_template("admin/index.html", **locals())
