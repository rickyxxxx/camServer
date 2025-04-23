from flask import Blueprint, render_template


bp = Blueprint('main', __name__)


@bp.route("/")
def index():
    return render_template("testing.html")


@bp.route("/debug")
def debug():
    return render_template("gallery.html")


