from flask import render_template, session, Blueprint, abort, request, flash, redirect, url_for
from models import User, Good
from helpers import user_required
from database import db
import os
import conf

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
    good.asso = request.form["asso"]
    good.semestre = request.form["semestre"]
    good.nb_exemplaires = request.form["exemplaires"]
    good.contenance = request.form["capacity"]
    good.commentaires = request.form["comment"]

    db.session.add(good)
    db.session.commit()
    db.session.flush()
    db.session.refresh(good)

    file = request.files['file']
    if file:
        extension = file.filename.split(".")[-1]
        file.save(os.path.join(conf.UPLOAD_FOLDER, str(good.id) + "." + extension))
        good.image_url = str(good.id) + "." + extension
        db.session.add(good)
        db.session.commit()

    flash("Écocup %s ajoutée" % good.nom, "success")

    return render_template("admin/index.html", **locals())


@bp.route('ecocup/edit', methods=["POST", "GET"])
@user_required
def edit():
    if not is_admin_connected():
        abort(401)

    if request.method == "GET":
        ecocup = Good.query.get(request.values["ecocup"])
        return render_template("admin/edit.html", **locals())
    else:
        ecocup = Good.query.get(request.form["ecocup"])
        for key in ["nom", "asso", "semestre", "nb_exemplaires", "contenance", "commentaires"]:
            if request.form[key] != "":
                setattr(ecocup, key, request.form[key])

        file = request.files['file']
        if file:
            extension = file.filename.split(".")[-1]
            file.save(os.path.join(conf.UPLOAD_FOLDER, str(ecocup.id) + "." + extension))
            ecocup.image_url = str(ecocup.id) + "." + extension
            db.session.add(ecocup)
            db.session.commit()

        db.session.commit()

    flash("Écocup %s modifiée" % ecocup.nom, "success")

    return render_template("admin/index.html", **locals())



@bp.route('ecocup/delete', methods=["POST"])
@user_required
def delete():
    if not is_admin_connected():
        abort(401)

    ecocup = Good.query.get(request.form["ecocup"])
    db.session.delete(ecocup)
    db.session.commit()

    return redirect(url_for("admin.index"))
