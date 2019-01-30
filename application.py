from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import os
import uuid
import requests

from helpers import *
import json

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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        return render_template("index.html")

    else:
        photos = photo_list_locations()
        return render_template("index.html", photos=photos)


@app.route("/login", methods=["GET", "POST"])
def login():
    # forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_id = inlog(username, password)

        # if username or password is missing or incorrect return an apology
        if user_id == "no_username":
            return apology("username is missing")
        elif user_id == "no_password":
            return apology("password missing")
        elif not user_id:
            return apology("username doesn't match password")

        session["user_id"] = user_id

        return redirect(url_for("index"))

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # forget any user_id
    session.clear()

    return redirect(url_for("login"))


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":

        username_confirmation = request.form.get("username2")
        answer_confirmation = request.form.get("securityquestion2")

        forgot = forgotpw(username_confirmation, answer_confirmation)

        # check if all fields are completed and correct
        if forgot == "fields_missing":
            return apology("not all fields are completed")
        elif forgot == "unvalid_username":
            return apology("Username doesn't exist")
        elif forgot == "no_match":
            return apology("Security answers don't match")

        session["user_id"] = forgot

        return redirect(url_for("changepw"))

    else:
        return render_template("forgot.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        answer = request.form.get("securityquestion")

        user = register_user(name, username, password, confirmation, answer)

        # ensure are fields are submitted and correct
        if user == "not_all_fields":
            return apology("not all fields all completed")
        elif user == "no_match":
            return apology("passwords don't match")
        elif user == "username_exists":
            return apology("username already exists")

        session["user_id"] = user

        return redirect(url_for("index"))

    else:
        return render_template("register.html")


@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    if request.method == "POST":

        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        change_pw = change_password(new_password, confirmation)

        # ensure all fields are submitted and correct
        if change_pw == "missing_field":
            return apology("not all fields are completed")
        elif change_pw == "no_match":
            return apology("passwords don't match")

        return redirect(url_for("index"))

    else:
        return render_template("changepw.html")


@app.route("/changeun", methods=["GET", "POST"])
@login_required
def changeun():
    if request.method == "POST":

        new_username = request.form.get("new_username")
        change_un = change_username(new_username)

        # make sure username is submitted and doesn't already exists
        if change_un == "no_username":
            return apology("must provide username")
        elif change_un == "username_exists":
            return apology("username already exists")

        return redirect(url_for("index"))

    else:
        return render_template("changeun.html")


@app.route("/follow", methods=["GET", "POST"])
@login_required
def follow():
    if request.method == 'POST':

        if request.form.get("follow"):

            location = request.form.get("location")
            followed_location = follow_location(location)

            # ensure a new location was submitted
            if followed_location == "no_location":
                return apology("location must be given")
            elif followed_location == "already_following":
                return apology("you already follow this location")

        else:
            location = request.form.get("unfollow location")
            unfollow_this_location = unfollow_location(location)

            # ensure location to unfollow was submitted
            if unfollow_this_location == "no_location":
                return apology("no location selected")

        return redirect(url_for("index"))

    else:
        followed_locations = list_following(session["user_id"])
        return render_template("follow.html", followed_locations=followed_locations)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == 'POST':

        folder = os.getcwd() + "/pics"
        allowed_extensions = ['.png', '.jpg', '.jpeg']
        file = request.files['image']
        extension = os.path.splitext(file.filename)[1]

        # check if an image is uploaded
        if extension not in allowed_extensions:
            return apology("extension not allowed")

        # ensure location was submitted
        if not request.form.get("location"):
            return apology("location must be given")

        # give every image a unique name
        file.filename = str(uuid.uuid4()) + extension
        photo = os.path.join(folder, file.filename)
        location = str(request.form.get("location")).lower().capitalize()

        photo_in_db(file.filename, location, request.form.get("caption"))

        file.save(photo)

        return redirect(url_for("index"))

    else:
        return render_template('upload.html')


@app.route("/comment", methods=["POST"])
def comment():
    if request.method == 'POST':

        cm_url = request.form['cm_url']
        photo_id = request.form['id']
        submit_comment(session["user_id"], photo_id, cm_url)
        return ""


@app.route('/uploads/<path:filename>')
def download_file(filename):
    # go to the folder with the pictures so u can show the pictures on the index with html
    path = os.getcwd() + "/pics"
    photo_path = os.path.join(path)

    return send_from_directory(photo_path, filename, as_attachment=True)


@app.route("/like", methods=["POST", "GET"])
@login_required
def like():
    # check if photo is liked
    if request.method == "POST":
        photo_id = request.form['id']
        liked = like_photo(session["user_id"], photo_id)
    else:
        photo_id = request.args.get("id")
        liked = is_liking_post(session['user_id'], photo_id)

    total_likes = likes_in_total(photo_id)
    return jsonify({'is_liked': liked, 'n_likes': total_likes})


@app.route("/zien_comments", methods=["POST", "GET"])
@login_required
def zien_comments():
    if request.method == "POST":
        global photo_id_comments
        photo_id_comments = request.form['photo_id']

        return photo_id_comments
    else:
        cmlist = show_comments(photo_id_comments)
        return jsonify(cmlist)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    naam = db.execute("SELECT name FROM users WHERE user_id=:user_id", user_id=session["user_id"])
    naam = naam[0]['name']

    return render_template('profile.html', naam=naam)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        location = str(request.form.get("location")).lower().capitalize()
        photos_list = search_location(location)

        return render_template("search.html", photos=photos_list)

    else:
        return render_template("search.html")
