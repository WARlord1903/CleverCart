from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from Web_Scrapper_InstacartV2 import search_items
import string
import random
import openai

app = Flask(__name__)

secret_key = ''

for i in range(255):
    secret_key += random.choice(string.ascii_letters)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = secret_key

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

db.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

def get_username():
    if current_user and current_user.is_authenticated:
        return current_user.username
    else:
        return ""

@app.route('/')
def homepage():
    return render_template('index.html', username=get_username())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    if session.get('was_once_logged_in'):
        del session['was_once_logged_in']
    flash('You have been logged out. Feel free to close the browser.')
    return redirect(url_for('homepage', username=get_username()))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"))
        
        db.session.add(user)

        db.session.commit()

        return redirect(url_for("login", username=get_username()))
    return render_template("register.html", username=get_username())

@app.route('/login', methods=["GET", "POST"])
def login():
    user = None
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for('homepage', username=get_username()))
        else:
            return render_template("login.html", failed=True, username=get_username())
    return render_template("login.html", failed=False, username=get_username())

@app.route('/search', methods=['POST'])
@login_required
def search():
    if request.method == "POST":
        ingredient = request.form.get("ingredient-search")
        items = search_items(ingredient)
        return render_template('search.html', search_term = ingredient, ingredient_list=items, username=get_username())
    return redirect(url_for('homepage', username=get_username()))

openai.api_key = "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"

@app.route('/recipe', methods=['GET', 'POST'])
@login_required
def recipe():
    if request.method == 'POST':
        recipe_name = request.form.get("recipe_name")

        # Call the custom GPT model to get ingredients for the recipe
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Custom GPT model ID
            messages=[
                {
                    "role": "system",
                    "content": "This GPT, Smart Chef, provides thoughtful recipe ideas and highlights ultra-processed ingredients."
                },
                {"role": "user", "content": f"List the ingredients for {recipe_name}"}
            ]
        )

        # Parse GPT response to extract ingredients
        ingredients_text = response['choices'][0]['message']['content']
        ingredients = ingredients_text.splitlines()  # Adjust parsing as needed based on GPT output format

        # Use web scraping to search for each ingredient
        ingredient_results = []
        for ingredient in ingredients:
            result = search_items(ingredient)
            ingredient_results.append({"ingredient": ingredient, "results": result})
        
        return render_template("recipe_results.html", ingredient_results=ingredient_results, username=get_username())
    
    return render_template("recipe_form.html", username=get_username())