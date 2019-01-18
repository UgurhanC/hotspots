import csv
import urllib.request

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
from passlib.apps import custom_app_context as pwd_context

db = SQL("sqlite:///hotspots.db")

def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def inlog(username, password):
    if not username:
        return apology("username missing")
    if not password:
        return apology("password missing")

    rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    # ensure username exists and password is correct
    if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
        return apology("username doesn't match password")

    inlog = rows[0]["user_id"]
    return inlog

def forgotpw(username_confirmation, answer_confirmation):
    # ensure username was submitted
    if not username_confirmation:
        return apology("must provide username")

    allusers = db.execute("SELECT username FROM users WHERE username = :username", username=username_confirmation)
    if not allusers:
        return apology("Username doesn't exist")

    # ensure security question has been answered
    elif not answer_confirmation:
        return apology("Must answer security question")

    temp = db.execute("SELECT securityquestion FROM users WHERE username = :username", username=username_confirmation)
    secquestion = temp[0]['securityquestion']
    if answer_confirmation != secquestion:
        return apology("Security answers don't match")

    return session_id(username_confirmation)

def session_id(username):
    ids = db.execute("SELECT * FROM users WHERE username = :username", username=username)
    if len(ids) > 0:
        return ids[0]["user_id"]