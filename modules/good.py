from flask import Blueprint, render_template, abort
from models import Good
from helpers import user_required


bp = Blueprint('good', __name__, url_prefix='/good/')


@bp.route('<int:good_id>')
@user_required
def summary(good_id):
    good = Good.query.get(good_id)
    if good is None:
        abort(404)

    return render_template("good/summary.html", **locals())
