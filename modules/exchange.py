from flask import render_template, url_for, redirect, session, flash, Blueprint, request
from helpers import user_required
from models import ExchangeMetadata, ExchangeData
from database import db
import datetime
from sqlalchemy import or_, and_


bp = Blueprint('exchange', __name__, url_prefix='/exchange/')


@bp.route('done')
@user_required
def exchanges():
    username = session["username"]

    user_exchanges = ExchangeMetadata.query.filter(
        or_(ExchangeMetadata.giver_id == username, ExchangeMetadata.receiver_id == username)).all()

    return render_template("echange/done.html", **locals())


@bp.route('')
@user_required
def index():
    username = session["username"]

    user_exchanges = ExchangeMetadata.query.filter(
        and_(ExchangeMetadata.giver_id == username, ExchangeMetadata.receiver_id == None)).all()

    return render_template("echange/index.html", **locals())


@bp.route('create', methods=["POST"])
@user_required
def create():

    metadata = ExchangeMetadata(session["username"])
    db.session.add(metadata)

    # Forced to flush & refresh to get the metadata.id
    db.session.flush()
    db.session.refresh(metadata)

    for good_id in request.form["giver_goods"]:
        data = ExchangeData(metadata.id, good_id, session["username"])
        db.session.add(data)

    for good_id in request.form["receiver_goods"]:
        data = ExchangeData(metadata.id, good_id, None)
        db.session.add(data)

    db.session.commit()

    return redirect("exchange.index")


@bp.route('delete')
@user_required
def delete():
    return render_template("echange/index.html", **locals())


@bp.route('details')
@user_required
def details():
    return render_template("echange/details.html", **locals())


@bp.route('confirm/<exchange_id>')
@user_required
def confirm(exchange_id):
    echange = ExchangeMetadata.query.get(exchange_id)

    if echange.date_execution is not None:
        return redirect(url_for("exchange.exchanges"))

    if session["username"] not in [echange.receiver_id, echange.giver_id]:
        flash("On ne peut pas confirmer un échange dans lequel on n’est pas impliqué", "danger")
        return redirect(url_for("exchange.exchanges"))

    if session["username"] == echange.giver_id:
        echange.date_conf_giver = datetime.datetime.now()
    else:
        echange.date_conf_receiver = datetime.datetime.now()

    if echange.date_conf_receiver is not None and echange.date_conf_giver is not None:
        flash("Échange confirmé !", "success")
        echange.date_execution = datetime.datetime.now()
    else:
        other = echange.giver_id if session["username"] == echange.receiver_id else echange.receiver_id
        flash("L’échange sera confirmé lorsque %s aura aussi confirmé" % other, "info")

    db.session.commit()

    return redirect(url_for("exchange.exchanges"))


@bp.route('cancel/<exchange_id>')
@user_required
def cancel(exchange_id):
    echange = ExchangeMetadata.query.get(exchange_id)

    if echange.date_execution is not None:
        flash("On ne peut pas annuler un échange effectué", "danger")
        return redirect(url_for("exchange.exchanges"))

    if session["username"] not in [echange.receiver_id, echange.giver_id]:
        flash("On ne peut pas annuler un échange dans lequel on n’est pas impliqué", "danger")
        return redirect(url_for("exchange.exchanges"))

    echange.date_cancelled = datetime.datetime.now()
    echange.canceller = session["username"]

    db.session.commit()
    flash("Échange annulé", "danger")
    compute(session["username"])

    return redirect(url_for("exchange.exchanges"))


def compute(user):
    """
    Computes all possible exchanges across the database.
    If an exchange concerns user, True is returned, otherwise
    False is returned
    """

    # List possible matches across all database
    requete = """
SELECT c1.login_user, c2.login_user, c1.good_id, c1.value, c1.id
FROM collection c1, collection c2
WHERE c1.has_it = 1 AND c2.wishes_it = 1
AND c1.locked = 0 AND c1.good_id = c2.good_id
ORDER BY c1.value DESC;"""

    db_matches = list(db.engine.execute(requete))

    # No possible match
    if len(db_matches) == 0:
        return False

    user_concerned = False
    for match in db_matches:
        giver, receiver, good_id, value, collec_id = match

        # Tries to complete a possible exchange by offering other goods
        goods_in_exchange = """
SELECT c1.good_id
FROM collection c1, collection c2
WHERE c1.login_user = '%s' AND c1.has_it = 1
AND c2.login_user = '%s' AND c1.locked = 0
AND c1.value = 1
AND c2.wishes_it AND c1.good_id = c2.good_id;
""" % (receiver, giver)
        possible_goods = [row[0] for row in db.engine.execute(goods_in_exchange)]
        if len(possible_goods) >= value:
            # Flags any exchange concerning the user
            if not user_concerned and user in [giver, receiver]:
                user_concerned = True
            do_exchange(giver, receiver, [good_id], possible_goods[:value])

    return user_concerned
