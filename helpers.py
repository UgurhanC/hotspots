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
    # check if username and password are given
    if not username:
        return "no_username"
    if not password:
        return "no_password"

    rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    # ensure username exists and password is correct
    if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
        return None

    return rows[0]["user_id"]


def forgotpw(username_confirmation, answer_confirmation):
    # ensure username was submitted
    if not username_confirmation:
        return "no_username"

    # check if username exists
    users = db.execute("SELECT username FROM users WHERE username = :username", username=username_confirmation)
    if not users:
        return "unvalid_username"

    # ensure security question has been answered
    elif not answer_confirmation:
        return "no_security_question"

    # check if the answer to the securtyquestion match
    answer = db.execute("SELECT securityquestion FROM users WHERE username = :username", username=username_confirmation)
    secquestion = answer[0]['securityquestion']
    if answer_confirmation != secquestion:
        return "no_match"

    return session_id(username_confirmation)


def session_id(username):
    # get the rows with the username that is given
    ids = db.execute("SELECT * FROM users WHERE username = :username", username=username)
    # if the username exists return the session
    if len(ids) > 0:
        return ids[0]["user_id"]

def register_user(name, username, password, confirmation, answer):
            # ensure name was submitted
        if not name:
            return "no_name"

        # ensure username was submitted
        elif not username:
            return "no_username"

        # ensure password was submitted
        elif not password:
            return "no_password"

        # ensure confirmation was submitted
        elif not confirmation:
            return "no_confirmation"

        # ensure password and confirmation are the same
        elif password != confirmation:
            return "no_match"

        # ensure security question has been answered
        elif not answer:
            return "no_answer"

        # check if username doesn't already exists
        if session_id(username):
            return "username_exists"

        # add name and username and password and securityquestion to database if username doesn't exist
        db.execute("INSERT INTO users (name, username, hash, securityquestion) values(:name, :username, :hash, :securityquestion)", name=request.form.get(
                   "name"), username=request.form.get("username"), hash=pwd_context.hash(request.form.get("password")), securityquestion=request.form.get("securityquestion"))

        ids = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # remember which user has logged in
        return ids[0]["user_id"]