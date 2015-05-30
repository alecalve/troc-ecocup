from flask import render_template, Blueprint
from helpers import user_required

bp = Blueprint('profil', __name__, url_prefix='/profil/')


@bp.route('')
@user_required
def me():
    return render_template("profil/index.html", **locals())
