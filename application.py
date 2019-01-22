from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import os
import uuid

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///hotspots.db")


@app.route("/")
@login_required
def index():
    # check which locations are followed
    following = db.execute("SELECT location FROM follows WHERE user_id=:user_id", user_id=session["user_id"])
    follow_list = []

    # make a list of the locations that are followed
    for follow in following:
        follow_list.append(follow["location"])

    search = "(" + str(follow_list)[1:-1] + ")"

    # make a list of photos of the followed locations and order by timestamp
    photos = []
    photo_dict = db.execute("SELECT filename FROM photo WHERE location IN {} ORDER BY timestamp DESC".format(search))
    for photo in photo_dict:
        photos.append(photo['filename'])

    return render_template("index.html", photos=photos)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # get the username and password
        username = request.form.get("username")
        password = request.form.get("password")

        user_id = inlog(username, password)

        # if username or password is missing return an apology
        if user_id == "no_username":
            return apology("username is missing")
        elif user_id == "no_password":
            return apology("password missing")

        # check if the username exists and if password is correct
        elif not user_id:
            return apology("username doesn't match password")

        session["user_id"] = user_id

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """forgot password."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username_confirmation = request.form.get("username2")
        answer_confirmation = request.form.get("securityquestion2")

        forgot = forgotpw(username_confirmation, answer_confirmation)

        if forgot == "no_username":
            return apology("must provide username")
        elif forgot == "unvalid_username":
            return apology("Username doesn't exist")

        # ensure security question has been answered
        elif forgot == "no_security_question":
            return apology("Must answer security question")
        elif forgot == "no_security_question":
            return apology("Security answers don't match")

        session["user_id"] = forgot

        return redirect(url_for("changepw"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("forgot.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        answer = request.form.get("securityquestion")

        user = register_user(name, username, password, confirmation, answer)

        # ensure name was submitted
        if user == "no_name":
            return apology("must provide name")

        # ensure username was submitted
        elif user == "no_username":
            return apology("must provide username")

        # ensure password was submitted
        elif user == "no_password":
            return apology("must provide password")

        # ensure confirmation was submitted
        elif user == "no_confirmation":
            return apology("must confirm password")

        # ensure password and confirmation are the same
        elif user == "no_match":
            return apology("passwords don't match")

        # ensure security question has been answered
        elif user == "no_answer":
            return apology("Must answer security question")

        # check if username doesn't already exists
        elif user == "username_exists":
            return apology("username already exists")

        session["user_id"] = user

        # redirect user to index page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    """Change the password."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure new password was submitted
        if not request.form.get("new_password"):
            return apology("must provide password")

        # ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password")

        # ensure password and confirmation are the same
        if request.form.get("new_password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        # update database delete old hash insert new hash
        result = db.execute("UPDATE users SET hash = :hash WHERE user_id=:user_id",
                            user_id=session["user_id"], hash=pwd_context.hash(request.form.get("new_password")))

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepw.html")


@app.route("/changeun", methods=["GET", "POST"])
@login_required
def changeun():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure new username was submitted
        if not request.form.get("new_username"):
            return apology("must provide username")

        # check if username doesn't already exists
        if session_id(request.form.get("new_username")):
            return apology("username already exists")

        # update database delete old username insert new username
        db.execute("UPDATE users SET username = :username WHERE user_id=:user_id",
                   user_id=session["user_id"], username=(request.form.get("new_username")))

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changeun.html")


@app.route("/follow", methods=["GET", "POST"])
@login_required
def follow():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        # ensure location was submitted
        if not request.form.get("location"):
            return apology("location must be given")

        location = request.form.get("location").lower().capitalize()

        # follow the location that was submitted
        db.execute("INSERT INTO follows (user_id, location) VALUES (:user_id, :location)",
                   user_id=session["user_id"], location=location)

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("follow.html")


@app.route("/like/<action>", methods=["GET", "POST"])
@login_required
def like(user_id, action):
    if action == 'like':
        session.user_id.like_photo(id)
    if action == 'unlike':
        session.user_id.unlike_photo(id)
    return render_template(index.html)


@app.route("/react", methods=["GET", "POST"])
@login_required
def react():
    return apology("todo")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    # else if user reached route via GET (as by clicking a link or via redirect)
    if request.method == 'POST':

        # go to the folder with the pictures
        UPLOAD_FOLDER = os.getcwd() + "/pics"

        ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg']
        file = request.files['image']
        extension = os.path.splitext(file.filename)[1]

        # check if an image is uploaded
        if extension not in ALLOWED_EXTENSIONS:
            return apology("extension not allowed")

        # ensure location was submitted
        if not request.form.get("location"):
            return apology("location must be given")

        # give every image a unique name
        file.filename = str(uuid.uuid4()) + extension
        photo = os.path.join(UPLOAD_FOLDER, file.filename)
        location = str(request.form.get("location")).lower().capitalize()

        # upload filename to database without caption
        if not request.form.get("caption"):
            db.execute("INSERT INTO photo (user_id, filename, location) VALUES (:user_id, :filename, :location)",
                       user_id=session["user_id"], filename=file.filename, location=location)

        # upload filename with caption
        else:
            db.execute("INSERT INTO photo (user_id, filename, location, caption) VALUES (:user_id, :filename, :location, :caption)",
                       user_id=session["user_id"], filename=file.filename, location=location, caption=request.form.get("caption"))

        file.save(photo)

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('upload.html')


@app.route('/uploads/<path:filename>')
def download_file(filename):
    # go to the folder with the pictures so u can show the pictures on the index with html
    path = os.getcwd() + "/pics"
    photo_path = os.path.join(path)
    return send_from_directory(photo_path, filename, as_attachment=True)
