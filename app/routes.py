from flask import Blueprint, render_template


DEBUG = True
bp = Blueprint('main', __name__)


@bp.route("/")
def index():
    if DEBUG:
        return render_template("testing.html")
    else:
        return render_template("gallery.html")

