from flask import render_template, url_for, redirect, session, flash, Blueprint
from helpers import user_required
from models import ExchangeMetadata, ExchangeData, User, Collection, Good
from database import db
import datetime
from sqlalchemy import or_


bp = Blueprint('exchange', __name__, url_prefix='/exchange/')


@bp.route('')
@user_required
def exchanges():
    username = session["username"]

    exchanges = ExchangeMetadata.query.filter(or_(ExchangeMetadata.giver_id == username, ExchangeMetadata.receiver_id == username)).all()

    return render_template("echange/index.html", **locals())


def do_exchange(giver_id, receiver_id, giver_goods, receiver_goods):
    """
    Do all what is needed for an exchange to be done:
        · locks the goods
        · creates the ExchangeMetadata
        · creates the ExchangeData
        · notifies the users
    """

    # Locking the goods
    for good_id in giver_goods + receiver_goods:
        collec = Collection.query.filter_by(login_user=giver_id, good_id=good_id).first()
        collec.locked = True

    for good_id in giver_goods + receiver_goods:
        collec = Collection.query.filter_by(login_user=receiver_id, good_id=good_id).first()
        collec.locked = True

    metadata = ExchangeMetadata(giver_id, receiver_id)
    db.session.add(metadata)

    # Forced to flush & refresh to get the metadata.id
    db.session.flush()
    db.session.refresh(metadata)

    for good_id in giver_goods:
        data = ExchangeData(metadata.id, good_id, giver_id)
        db.session.add(data)
 
    for good_id in receiver_goods:
        data = ExchangeData(metadata.id, good_id, receiver_id) 
        db.session.add(data)

    #TODO notify users
    db.session.commit()


@bp.route("compute")
@user_required
def compute():
    # List possible matches across all database
    requete = """
SELECT c1.login_user, c2.login_user, c1.good_id, c1.value
FROM collection c1, collection c2
WHERE c1.has_it = 1 AND c2.wishes_it = 1
AND c1.locked = 0 AND c1.good_id = c2.good_id
ORDER BY c1.value DESC;"""

    db_matches = list(db.engine.execute(requete))

    if len(db_matches) == 0:
        return redirect(url_for("collection.mine"))


    for match in db_matches:
        giver_id, receiver_id, good_id, value = match
        # Check if good is not locked in a previous exchange
        g = Collection.query.get(good_id)
        if g.locked:
            continue

        goods_in_exchange = """
SELECT c1.good_id
FROM collection c1, collection c2
WHERE c1.login_user = '%s' AND c1.has_it = 1 
AND c2.login_user = '%s' AND c1.locked = 0
AND c1.value = 1
AND c2.wishes_it AND c1.good_id = c2.good_id;
""" % (receiver_id, giver_id)
        possible_goods = [row[0] for row in db.engine.execute(goods_in_exchange)]
        if len(possible_goods) >= value:
            do_exchange(giver_id, receiver_id, [good_id], possible_goods[:value])

    return redirect(url_for("collection.mine"))


@bp.route('confirm/<int:id>')
@user_required
def confirm(id):
    echange = ExchangeMetadata.query.get(id)

    if username == echange.user1:
        echange.date_conf1 = datetime.datetime.utcnow()
    else:
        echange.date_conf2 = datetime.datetime.utcnow()

    if echange.date_conf1 is not None and echange.date_conf2 is not None:
        flash("Échange confirmé !", "success")
        echange.date_execution = datetime.datetime.utcnow()

    db.session.commit()

    return redirect(url_for("echange.echanges"))


@bp.route('cancel/<int:id>')
@user_required
def cancel(id):
    echange = Exchange.query.get(id)

    echange.date_cancelled = datetime.datetime.utcnow()
    echange.canceller = username

    if echange.date_conf1 is not None and echange.date_conf2 is not None:
        echange.date_execution = datetime.datetime.utcnow()

    good1 = Collection.query.filter_by(
        login_user=echange.user1, good=echange.good1).first()
    good12 = Collection.query.filter_by(
        login_user=echange.user1, good=echange.good2).first()
    good2 = Collection.query.filter_by(
        login_user=echange.user2, good=echange.good2).first()
    good21 = Collection.query.filter_by(
        login_user=echange.user2, good=echange.good1).first()

    good1.in_collection = 1
    good1.souhaite = 0
    good1.accepte_echange = 0

    good12.in_collection = 0
    good12.souhaite = 1
    good12.accepte_echange = 0

    good2.in_collection = 1
    good2.souhaite = 0
    good2.accepte_echange = 0

    good21.in_collection = 0
    good21.souhaite = 1
    good21.accepte_echange = 0

    db.session.commit()
    flash("Échange annulé", "danger")

    return redirect(url_for("echange.compute"))
