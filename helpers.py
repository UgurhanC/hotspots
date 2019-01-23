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

    # ensure username and answer were submitted
    if not username_confirmation or not answer_confirmation:
        return "fields_missing"

    # check if username exists
    users = db.execute("SELECT username FROM users WHERE username = :username", username=username_confirmation)
    if not users:
        return "unvalid_username"

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
    # ensure all fields where submitted
    if not name or not username or not password or not confirmation or not answer:
        return "not_all_fields"

    # ensure password and confirmation are the same
    elif password != confirmation:
        return "no_match"

    # check if username doesn't already exists
    if session_id(username):
        return "username_exists"

    # add name and username and password and securityquestion to database if username doesn't exist
    db.execute("INSERT INTO users (name, username, hash, securityquestion) values(:name, :username, :hash, :securityquestion)", name=request.form.get(
               "name"), username=request.form.get("username"), hash=pwd_context.hash(request.form.get("password")), securityquestion=request.form.get("securityquestion"))

    ids = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
    # remember which user has logged in
    return ids[0]["user_id"]


def change_password(new_password, confirmation):
    # ensure all fields are submitted
    if not new_password or not confirmation:
        return "missing_field"

    # ensure password and confirmation are the same
    if new_password != confirmation:
        return "no_match"

    # update database delete old hash insert new hash
    result = db.execute("UPDATE users SET hash = :hash WHERE user_id=:user_id",
                        user_id=session["user_id"], hash=pwd_context.hash(request.form.get("new_password")))

    return "password_changed"


def change_username(new_username):
    # ensure new username was submitted
    if not new_username:
        return "no_username"

    # check if username doesn't already exists
    if session_id(new_username):
        return "username_exists"

    # update database delete old username insert new username
    db.execute("UPDATE users SET username = :username WHERE user_id=:user_id",
               user_id=session["user_id"], username=(request.form.get("new_username")))

    return "username_changed"


def follow_location(location):
    # check if location was submitted
    if not location:
        return "no_location"

    place = location.lower().capitalize()

    followed = db.execute("SELECT location FROM follows WHERE location=:location", location=place)
    if len(followed) > 0:
        return "already_following"

    # follow the location that was submitted
    db.execute("INSERT INTO follows (user_id, location) VALUES (:user_id, :location)",
               user_id=session["user_id"], location=place)

    return "location_followed"

def like_photo(user_id, id):
    if is_liking_post(user_id, id) == True:
        db.execute("INSERT INTO liked (user_id, id) VALUES (:user_id, :id)",
            user_id=user_id, id=id)
    elif is_liking_post(user_id, id) == False:
        db.execute("DELETE FROM liked WHERE user_id=:user_id and id=:id",
            user_id=user_id, id=id)

def is_liking_post(user_id, id):
    like_status = db.execute("SELECT user_id FROM liked WHERE id=:id", id=id)
    if {'user_id': user_id} in like_status:
        return False
    else:
        return True

def photo_in_db(filename, location, caption):
        # upload filename to database without caption
        if not caption:
            db.execute("INSERT INTO photo (user_id, filename, location) VALUES (:user_id, :filename, :location)",
                       user_id=session["user_id"], filename=filename, location=location)

        # upload filename with caption
        else:
            db.execute("INSERT INTO photo (user_id, filename, location, caption) VALUES (:user_id, :filename, :location, :caption)",
                       user_id=session["user_id"], filename=filename, location=location, caption=caption)

def list_following(user_id):
    return db.execute("SELECT location FROM follows WHERE user_id=:user_id GROUP BY location", user_id=user_id)
