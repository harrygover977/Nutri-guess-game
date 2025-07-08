from flask import render_template, request, session, flash
from flask import redirect, url_for
import json
import random
from datetime import date
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from main import db, login_manager


with open("data/foods.json", "r") as file:
    foods = json.load(file)

valid_foods = [food["name"] for food in foods]


def random_food():
    meal_list = []
    for food in foods:
        meal_list.append(food["name"])

    random_meal = random.choice(meal_list)
    return random_meal


def init_routes(app):
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/", methods=["GET", "POST"])
    def start_game():
        today = date.today()
        today_key = today.strftime("%Y-%m-%d")

        # Check if user has already played today
        if session.get("last_played_date") == today_key:
            # Check if they've completed the game (won or lost)
            game_completed = session.get("game_completed", False)

            if game_completed:
                # User has completed today's game, redirect to appropriate result page
                answer = session.get("answer")
                attempts = session.get("attempts", 1)

                if session.get("game_won", False):
                    return render_template(
                        "correct.html", answer=answer, attempts=attempts - 1
                    )
                else:
                    return render_template(
                        "incorrect.html", answer=answer, attempts=attempts - 1
                    )
            else:
                # User has started but not completed today's game, show current state
                answer = session.get("answer")
                clues = session.get("clues", [])
                attempts = session.get("attempts", 1)
                guesses = session.get("guesses", [])

                return render_template(
                    "index.html",
                    clues=clues[:attempts],
                    guesses=reversed(guesses),
                    guessed=False,
                )

        # New day, start a new game
        index = today.toordinal() % len(foods)
        food = foods[index]

        clues = [
            food["clue1"],
            food["clue2"],
            food["clue3"],
            food["clue4"],
            food["clue5"],
        ]

        # store state in session
        session["answer"] = food["name"]
        session["clues"] = clues
        session["attempts"] = 1
        session["guesses"] = []
        session["last_played_date"] = today_key
        session["game_completed"] = False
        session["game_won"] = False

        return render_template(
            "index.html",
            clues=[clues[0]],
            message="",
            guessed=False,
        )

    @app.route("/guess", methods=["GET", "POST"])
    def make_guess():
        guess = request.form.get("guess").strip().lower()
        answer = session.get("answer")
        clues = session.get("clues", [])
        attempts = session.get("attempts", 1)
        guesses = session.get("guesses", [])

        # Check if guess is valid (including with/without 's')
        is_valid_guess = False
        normalized_guess = guess

        # Check exact match first
        if guess in valid_foods:
            is_valid_guess = True
        # Check if adding 's' makes it valid
        elif guess + "s" in valid_foods:
            is_valid_guess = True
            normalized_guess = guess + "s"
        # Check if removing 's' makes it valid
        elif guess.endswith("s") and guess[:-1] in valid_foods:
            is_valid_guess = True
            normalized_guess = guess[:-1]

        if not is_valid_guess:
            flash("Invalid guess. Please try again!")
            return render_template(
                "index.html",
                clues=clues[:attempts],
                guesses=reversed(guesses),
                guessed=False,
            )

        # Use normalized guess for duplicate checking and comparison
        if normalized_guess in guesses:
            flash("You have already guessed that food. Try again!")
            return render_template(
                "index.html",
                clues=clues[:attempts],
                guesses=reversed(guesses),
                guessed=False,
            )

        # Add normalized guess to previous guesses list and increase attempts by 1
        guesses.append(normalized_guess)
        session["guesses"] = guesses
        attempts += 1
        session["attempts"] = attempts

        # End the game if the guess is correct or if attempts exceed 5
        if normalized_guess == answer:
            return redirect(url_for("correct_guess"))

        if attempts >= 6:
            return redirect(url_for("incorrect_guess"))

        return render_template(
            "index.html",
            clues=clues[:attempts],
            message="",
            guessed=False,
            guesses=reversed(guesses),
        )

    @app.route("/skip", methods=["POST"])
    def skip():
        session["attempts"] += 1
        return redirect(url_for("start_game"))

    @app.route("/correct", methods=["GET"])
    def correct_guess():
        answer = session.get("answer")
        attempts = session.get("attempts")
        # Mark game as completed and won
        session["game_completed"] = True
        session["game_won"] = True

        return render_template("correct.html", answer=answer, attempts=attempts - 1)

    @app.route("/incorrect", methods=["GET"])
    def incorrect_guess():
        answer = session.get("answer")
        attempts = session.get("attempts")
        # Mark game as completed and lost
        session["game_completed"] = True
        session["game_won"] = False

        return render_template("incorrect.html", answer=answer, attempts=attempts)

    @app.route("/signup", methods=["POST", "GET"])
    def signup():
        if request.method == "POST":
            email = request.form.get("email")
            username = request.form.get("username")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if User.query.filter_by(email=email).first():
                flash("Email already exists")
                return render_template("signup.html")

            if User.query.filter_by(username=username).first():
                flash("Username already exists")
                return render_template("signup.html")

            if len(password) < 8:
                flash("Password must be at least 8 characters long")
                return render_template("signup.html")

            if password != confirm_password:
                flash("Passwords do not match")
                return render_template("signup.html")

            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password),
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully")
            login_user(new_user)
            return redirect(url_for("start_game"))

        return render_template("signup.html")

    @app.route("/login", methods=["POST", "GET"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("start_game"))
            else:
                flash("Invalid email or password")
                return render_template("login.html")

        return render_template("login.html")

    @app.route("/reset")
    def reset():
        session.clear()
        return redirect(url_for("start_game"))
