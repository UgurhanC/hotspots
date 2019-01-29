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
#print(json.dumps(data, sort_keys=True, indent=4))
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
        #photo_id = request.form['id']
        #cmlist = show_comments(photo_id)
        #for cm in cmlist:
         #   print(cm)

        return render_template("index.html")

    else:
    # check which locations are followed
        following = db.execute("SELECT location FROM follows WHERE user_id=:user_id", user_id=session["user_id"])
        follow_list = []

        # make a list of the locations that are followed
        for follow in following:
            follow_list.append(follow["location"])

        search = "(" + str(follow_list)[1:-1] + ")"

        # make a list of photos of the followed locations and order by timestamp
        photos = []
        photo_dict = db.execute("SELECT filename, id, location FROM photo WHERE location IN {} ORDER BY timestamp DESC".format(search))
        for photo in photo_dict:
            likes = db.execute("SELECT COUNT (id) FROM liked WHERE id=:id", id=photo["id"])
            for like in likes:
                photos.append([photo["filename"], photo["id"], photo["location"], like["COUNT (id)"]])


        #print(comments)
        #print(comments_dict)
        # cdict json dict error
        '''
        cdict = {}
        for comment in comments_dict:
            if not comment['photo_id'] in cdict:
                cdict[comment['photo_id']] = []
                cdict[comment['photo_id']].append((comment['cm_url'], comment['user_id']))
            else:
                cdict[comment['photo_id']].append((comment['cm_url'], comment['user_id']))
        print(cdict)
        #print(json.dumps(cdict,ensure_ascii=False))
        cdict2 = json.dumps(cdict)
        print(type(cdict2))
        '''


        return render_template("index.html", photos=photos)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log user in.
    """

    # forget any user_id
    session.clear()

    if request.method == "POST":
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

        # check if all fields are completed
        if forgot == "fields_missing":
            return apology("not all fields are completed")

        # check if the username is valid
        elif forgot == "unvalid_username":
            return apology("Username doesn't exist")
        # check if the answer to the security question match
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

        # ensure are fields are submitted
        if user == "not_all_fields":
            return apology("not all fields all completed")

        # ensure password and confirmation are the same
        elif user == "no_match":
            return apology("passwords don't match")

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

        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        change_pw = change_password(new_password, confirmation)

        # ensure all fields are submitted
        if change_pw == "missing_field":
            return apology("not all fields are completed")
        # ensure passwords match
        elif change_pw == "no_match":
            return apology("passwords don't match")

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

        new_username = request.form.get("new_username")
        change_un = change_username(new_username)

        # make sure username is submitted and doesn't already exists
        if change_un == "no_username":
            return apology("must provide username")
        elif change_un == "username_exists":
            return apology("username already exists")

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

        # if a user wants to follow a new location
        if request.form.get("follow"):

            location = request.form.get("location")
            # follow the location
            followed_location = follow_location(location)

            # ensure location was submitted
            if followed_location == "no_location":
                return apology("location must be given")
            # check if user doesn't already follows the location
            elif followed_location == "already_following":
                return apology("you already follow this location")

        # if the user wants to unfollow a location
        else:

            location = request.form.get("unfollow location")
            # unfollow the location
            unfollow_this_location = unfollow_location(location)

            # ensure location to unfollow was submitted
            if unfollow_this_location == "no_location":
                return apology("no location selected")

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        followed_locations = list_following(session["user_id"])
        return render_template("follow.html", followed_locations=followed_locations)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    # else if user reached route via GET (as by clicking a link or via redirect)
    if request.method == 'POST':

        # go to the folder with the pictures
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

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('upload.html')


@app.route("/giphy", methods=["GET", "POST"])
def giphy():
    if request.method == 'POST':

        q = request.form.get("q")
        print(q)
        return render_template('index.html')
    else:
        return render_template('giphy.html')


@app.route("/indexgoed")
# @login_required
def indexgoed():
    df = pd.read_excel('worldcities.xlsx', sheet_name=0)  # can also index sheet by name or fetch all sheets
    mylist = df['city_ascii'].tolist()
    #mylist = json.dumps(mylist)

    if request.method == "POST":
        return render_template("indexgoed.html")
    else:
       # print(citylist())
        return render_template("indexgoed.html", mylist=mylist)

@app.route("/comment", methods=["POST"])
def comment():
    if request.method == 'POST':

        cm_url = request.form['cm_url']
        photo_id = request.form['id']
        submit_comment(session["user_id"], photo_id, cm_url)
        return ""


@app.route("/tstgif", methods=["GET", "POST"])
def tstgif():
    if request.method == 'POST':

        url = request.get_json()
        link = url['link']
        print(link)
        db.execute("INSERT INTO comment (c_url) VALUES (:link)", link=link)
        return render_template('tstgif.html')

    else:
        print(request.endpoint)
        return render_template('tstgif.html')


@app.route('/uploads/<path:filename>')
def download_file(filename):
    # go to the folder with the pictures so u can show the pictures on the index with html
    path = os.getcwd() + "/pics"
    photo_path = os.path.join(path)
    print(photo_path)
    return send_from_directory(photo_path, filename, as_attachment=True)


@app.route("/like", methods=["POST", "GET"])
@login_required
def like():
    if request.method == "POST":
        photo_id = request.form['id']
        like_photo(session["user_id"], photo_id)
        return ""
    else:
        jalike = db.execute("SELECT * FROM liked WHERE id=:photo_id AND user_id=:user_id",
                                photo_id=photo_id_comments, user_id=session["user_id"])
        yayor = []
        for x in jalike:
            yayor.append(x['id'])
        likedor = len(jalike)
        print(likedor, jalike, yayor)
        return jsonify(yayor)


@app.route("/load_comments", methods=["POST", "GET"])
@login_required
def load_comments():

    '''
        photo_id = request.form['photo_id']
        print(photo_id)
        cmlist = show_comments(photo_id)
        print(cmlist)
        return cmlist
    '''

    photo_id = request.form['photo_id']
    cmlist = show_comments(photo_id)
    print(cmlist, type(cmlist))
    return jsonify(cmlist)




    '''
            photo_id = request.form['id']
            cmlist2 = show_comments(photo_id)
            return jsonify(cmlist = cmlist2)
        else:
            photo_id = request.form['id']
            cmlist2 = show_comments(photo_id)
            return jsonify(cmlist = cmlist2)
    '''





@app.route("/zien_comments", methods=["POST", "GET"])
@login_required
def zien_comments():
    #photo_id = request.form['photo_id']
    #photo_id = 0
    if request.method == "POST":
        #photo_id = request.form['photo_id']
        #show_comments(photo_id)
        global photo_id_comments
        photo_id_comments = request.form['photo_id']
        #print(photo_id)
        return photo_id_comments
    else:
        #print(photo_id)
        comments_dict = db.execute("SELECT cm_url FROM comments WHERE photo_id=:photo_id",
                                photo_id=photo_id_comments)
        cmlist = []
        for comment in comments_dict:
            cmlist.append(comment['cm_url'])
        return jsonify(cmlist)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    naam = db.execute("SELECT name FROM users WHERE user_id=:user_id", user_id=session["user_id"])
    naam = naam[0]['name']
    return render_template('profile.html', usernaampje=naam)