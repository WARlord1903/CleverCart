from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from Web_Scraper_InstacartV3 import search_items
from databasefinal import fetch_items
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
    api_key = db.Column(db.String(256), nullable=True)
    preferred_store = db.Column(db.Integer, nullable=False)

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
    if current_user.is_authenticated:
        return render_template('home.html', username=get_username())
    else:
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
                     password=request.form.get("password"),
                     api_key='',
                     preferred_store=0)
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
            return redirect(url_for('home', username=get_username()))
        else:
            return render_template("login.html", failed=True, username=get_username())
    return render_template("login.html", failed=False, username=get_username())

@app.route('/account')
@login_required
def account_settings():
    if current_user.is_authenticated:
        return render_template("settings.html", username=get_username(), api_key=current_user.api_key, store=current_user.preferred_store)

@app.route('/account/password-update', methods=["POST"])
@login_required
def update_password():
    if current_user.is_authenticated:
        if request.form.get('password') == request.form.get('password-verification'):
            db.session.query(Users).filter(Users.id == current_user.get_id()).update({'password': request.form.get('password')})
            db.session.commit()
        return render_template("settings.html", username=get_username(), api_key=current_user.api_key, store=current_user.preferred_store)

@app.route('/account/key-update', methods=["POST"])
@login_required
def update_key():
    if current_user.is_authenticated:
        db.session.query(Users).filter(Users.id == current_user.get_id()).update({'api_key': request.form.get('api-key')})
        db.session.commit()
        return render_template("settings.html", username=get_username(), api_key=current_user.api_key, store=current_user.preferred_store)

@app.route('/account/update-store', methods=['POST'])
@login_required
def update_store():
    if current_user.is_authenticated:
        db.session.query(Users).filter(Users.id == current_user.get_id()).update({'preferred_store': int(request.form.get('store-options'))})
        db.session.commit()
        return render_template("settings.html", username=get_username(), api_key=current_user.api_key, store=current_user.preferred_store)


@app.route('/account/delete', methods=['POST'])
@login_required
def delete_account():
    id = current_user.get_id()
    logout_user()
    db.session.query(Users).filter(Users.id == id).delete()
    db.session.commit()
    return redirect('/')

@app.route('/')
def welcome_page():
    # Check if the user is already authenticated
    if current_user.is_authenticated:
        # Redirect to the main page if logged in
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/search', methods=['POST'])
@login_required
def search():
    
    ingredient = request.form.get("ingredient-search")
    items = search_items(ingredient, current_user.preferred_store) if ingredient else []
    return render_template('home.html', search_term=ingredient, ingredient_list=items, username=get_username())

@app.route('/home')
@login_required
def home():
    openai.api_key = current_user.api_key
    return render_template('home.html', username=get_username())

@app.route('/chat', methods=['POST'])
@login_required
def chat_with_openai():
    user_message = request.json.get("message")
    if user_message:
        client = openai.Client(api_key=current_user.api_key)
        
        # Define behavior instructions for the assistant in the system message
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "is this a good instruction for it: This GPT, Smart Chef, provides thoughtful recipe ideas, pairing suggestions, and price comparisons from external databases. It avoids recommending unsafe or non-digestible ingredients (such as inedible items like socks). Smart Chef highlights when recipes contain ultra-processed ingredients, giving users the option to substitute healthier alternatives whenever possible. While it generally emphasizes fresh and healthier ingredients, Smart Chef recognizes that certain dishes, like desserts or complex recipes like turkey stuffing, may require the use of some ultra-processed ingredients, and it offers flexibility accordingly. Smart Chef has a friendly, encouraging tone, designed to boost the user's confidence in the kitchen. When a user requests a recipe, like for salmon or any other dish, Smart Chef follows up by asking if they'd prefer a complex dish with multiple ingredients or a simpler one with fewer, more basic ingredients. Additionally, Smart Chef will always offer to suggest side dishes to complement the entree. Smart Chef is approachable, sensitive to ingredient accessibility, and offers supportive, thoughtful guidance to make cooking a positive experience, regardless of what the user has on hand."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        # Convert response to dictionary and extract bot's reply
        response_dict = response.to_dict()
        bot_reply = response_dict['choices'][0]['message']['content']
        return jsonify({"reply": bot_reply})
    return jsonify({"error": "No message provided"}), 400


@app.route('/recipe', methods=['GET', 'POST'])
@login_required
def recipe():
    
    if request.method == 'POST':
        recipe_name = request.form.get("recipe_name")

        client = openai.Client(api_key=current_user.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "This GPT, Smart Chef, provides thoughtful recipe ideas and highlights ultra-processed ingredients."
                },
                {"role": "user", "content": f"If {recipe_name} is not edible, output \"None\". Otherwise, list the ingredients for {recipe_name} without any greetings, with each ingredient on a new line. If an ingredient contains more than one product (e.g. salt and pepper), split them up."},
            ]
        )

        ingredients_text = response.to_dict()['choices'][0]['message']['content']

        if ingredients_text == "None":
            return render_template("recipe_form.html", failed=True, username=get_username())

        if ingredients_text[:2] == '- ':
            ingredients = [ing[2:] for ing in ingredients_text.splitlines()]
        else:
            ingredients = ingredients_text.splitlines()
            
        ingredient_str = ''
        for i in ingredients:
            ingredient_str += i + ', '
        i = i[:-2]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"List the listed ingredients without any greetings, amounts, or other kinds of description (just the names of the ingredients), with each ingredient on a separate line: [{ingredient_str}]. Ensure that each ingredient name is as simple as possible. Ensure that each item in the list in the prompt has exactly one corresponding item in the response (The given list and the resulting list should have the same length)."},
            ]
        )

        raw_ingredients_text = response.to_dict()['choices'][0]['message']['content']
        if raw_ingredients_text[:2] == '- ':
            raw_ingredients = [ing[2:] for ing in raw_ingredients_text.splitlines()]
        else:
            raw_ingredients = raw_ingredients_text.splitlines()
        
        return render_template("recipe_results.html", recipe=recipe_name, ingredients=ingredients, ingredient_names=raw_ingredients, username=get_username())
    
    return render_template("recipe_form.html", failed=False, username=get_username())

@app.route('/recipe/search/', methods=['POST'])
@login_required
def recipe_ingredient_search():
    ingredient = request.json.get('ingredient')
    cached_items = fetch_items(ingredient, ["publix", "food-city", "kroger", "sams-club", "food-lion", "aldi"][current_user.preferred_store])
    if len(cached_items) == 0:
        items = search_items(ingredient, current_user.preferred_store)
    else:
        items = cached_items
    items = [list(i) for i in items]
    return jsonify(items)

@app.route('/recipe/update/', methods=['POST'])
@login_required
def recipe_ingredient_update():
    ingredient = request.json.get('ingredient')
    items = search_items(ingredient, current_user.preferred_store)
    items = [list(i) for i in items]
    return jsonify(items)

@app.route('/recipe/steps/', methods=['POST'])
@login_required
def recipe_generate_steps():
    ingredients = request.json.get('ingredients')
    recipe = request.json.get('recipe')
    
    ingredient_str = ""
    for i in ingredients:
        ingredient_str += i + ", "
    ingredient_str = ingredient_str[:-2]

    client = openai.Client(api_key=current_user.api_key)
        
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "This GPT is given the name of recipe and a list of ingredients, and provides step-by step instructions on how to make the recipe in the form of an ordered list."
            },
            {
                "role": "user",
                "content": f"How can I make {recipe} using the following ingredients: [{ingredient_str}]?"
            }
        ]
    )
    
    # Convert response to dictionary and extract bot's reply
    response_dict = response.to_dict()
    step_list = response_dict['choices'][0]['message']['content'].splitlines()
    steps = []

    for step in step_list:
        if step.strip() != "":
            new_step = ""
            split_step = step.split('. ')
            for i in range(1, len(split_step)):
                   new_step += split_step[i] + '. '
            steps.append(new_step[:-2])
    steps = list(filter(None, steps))
    return jsonify(steps)