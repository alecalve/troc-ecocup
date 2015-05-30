import pkgutil
import importlib
from functools import wraps

from flask import Blueprint, session, redirect, url_for


def user_required(f):
    """ Décorateur qui vérifie si un utilisateur est loggé et sinon redirige vers le CAS """

    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            assert(session["logged_in"] is True)
        except AssertionError:
            return redirect(url_for("cas.login"))
        except KeyError:
            return redirect(url_for("cas.login"))
        return f(*args, **kwargs)
    return decorator


# https://github.com/mattupstate/overholt/blob/master/overholt/helpers.py (MIT license)
def register_blueprints(app, package_name=None, package_path="."):
    """Register all Blueprint instances on the specified Flask application found
    in all modules for the specified package.

    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path
    """

    for _, name, _ in pkgutil.iter_modules(package_path):
        import_string = '%s.%s' % (package_name, name) if package_name else name
        m = importlib.import_module(import_string)
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
