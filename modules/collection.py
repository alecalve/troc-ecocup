from flask import render_template, url_for, redirect, request, session, flash, Blueprint
from models import User, Collection, Good
from helpers import user_required
from database import db
from modules.exchange import compute


bp = Blueprint('collection', __name__, url_prefix='/collection/')


@bp.route('')
@user_required
def mine():
    """ Affiche la collection de l’utilisateur connecté """

    has = User.query.get(session["username"]).collections.filter_by(has_it=True).all()
    wishes = User.query.get(session["username"]).collections.filter_by(wishes_it=True).all()
    ecocups = Good.query.all()

    return render_template("collection/index.html", **locals())


@bp.route('add', methods=["POST"])
@user_required
def add():
    """
    Met à jour la collection de l’utilisateur connecté. Si un échange a lieu, redirige vers la
    page des échanges
    """

    ecocup = Good.query.get(request.form["ecocup"])
    if ecocup is not None:
        # Check first if the ecocup is not already in the user’s collection
        collec = Collection.query.filter_by(login_user=session["username"], good_id=request.form["ecocup"]).first()
        if collec is not None:
            flash("Cette écocup est déjà dans ta collection", "warning")
            return redirect(url_for("collection.mine"))
        else:
            collec = Collection(session["username"], ecocup.id)
            collec.value = request.form["value"]
            if request.form["type"] == "has":
                collec.has_it = True
                collec.wishes_it = False
            else:
                collec.has_it = False
                collec.wishes_it = True

            db.session.add(collec)
            db.session.commit()

        exchange_happened = compute(session["username"])
        if exchange_happened:
            return redirect(url_for("exchange.exchanges"))

    return redirect(url_for("collection.mine", _anchor=request.form["type"]))


@bp.route('delete', methods=["POST"])
@user_required
def delete():
    """ Met à jour la collection de l’utilisateur connecté """

    collec = Collection.query.filter_by(login_user=session["username"], good_id=request.form["good"]).first()
    if collec is not None and not collec.locked:
        db.session.delete(collec)
        db.session.commit()
    return redirect(url_for("collection.mine"))