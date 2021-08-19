# Condition 1. WHen the user gives the database the long url then the db will return short url if it contains it, else it will generate a new short url by generating a new three random alphabets.
# Condition 2. When the user gives the db the short url then db will check if there exists long url corresponding to it, if there is then it will redirect the user to the long url page.


# from flask import Flask, render_template
# app = Flask(__name__)

# @app.route('/')     # decorator
# def hello_world():
#     return render_template("home.html")


# @app.route('/anish')
# def hello_anish():
#     return "hello_anish"

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)


from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os
#os.environ.get('DATABASE_URL')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # we don't need to track modifications 

db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    db.create_all()    # create cols inside the database

class Urls(db.Model):   # creating database model 
    id_ = db.Column("id_", db.Integer, primary_key=True)     # (name of the col, type of col, primary key)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(10))

    def __init__(self, long, short):
        self.long = long
        self.short = short

def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase  # to get a broader range to choose from
    while True:
        rand_letters = random.choices(letters, k=3)    # choose 3 random letters
        rand_letters = "".join(rand_letters)    # bcz the letters will be in a list
        short_url = Urls.query.filter_by(short=rand_letters).first()    # if the combination of letters already exists, if exists make a new combination
        if not short_url: 
            return rand_letters


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        url_received = request.form["nm"]
        found_url = Urls.query.filter_by(long=url_received).first()

        if found_url:
            return redirect(url_for("display_short_url", url=found_url.short))
        else:
            short_url = shorten_url()
            print(short_url)
            new_url = Urls(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()   # make the changes permenant 
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('home.html')

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1>Url doesnt exist</h1>'

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display=url)

@app.route('/all_urls')
def display_all():
    return render_template('all_urls.html', vals=Urls.query.all())

if __name__ == '__main__':
    app.run(port=5000, debug=True)