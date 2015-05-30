from flask import render_template, session, Blueprint, jsonify, send_from_directory
from helpers import user_required
from database import db
from models import Good, ExchangeMetadata, Like
import conf

bp = Blueprint('base', __name__, url_prefix='/')


@bp.route('')
@user_required
def index():
    last_exchanges = ExchangeMetadata.query.filter(
        ExchangeMetadata.date_execution != None).order_by(ExchangeMetadata.date_execution).limit(10)
    last_exchanges = list(last_exchanges)
    goods = list(enumerate(Good.query.all()))
    return render_template("base/index.html", **locals())


@bp.route('comment-ca-marche')
@user_required
def comment_ca_marche():
    return render_template('base/comment.html')


@bp.route('like/<int:good>')
@user_required
def like(good, value=1):
    like_item = Like.query.filter_by(user=session["username"], good=good).first()

    if like_item is None:
        like_item = Like(user=session["username"], good=good, valeur=1)
        db.session.add(like_item)
    else:
        like_item.valeur = value

    good = Good.query.get(good)

    if good is None:
        return jsonify({"error": True})

    db.session.commit()
    good.appreciation = sum(map(lambda l: l.valeur, Like.query.filter_by(good=good.id).all()))
    db.session.commit()
    return jsonify({"appreciation": good.appreciation, "error": False})


@bp.route('dislike/<int:good>')
@user_required
def dislike(good):
    return like(good, value=-1)


@bp.route('uploads/<string:filename>')
def image(filename):
    return send_from_directory(conf.UPLOAD_FOLDER, filename)
