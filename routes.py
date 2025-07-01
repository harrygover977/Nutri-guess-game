from flask import Flask, render_template, request, session, flash
from flask import redirect, url_for
import json
import random
from datetime import date

with open("data/foods.json", "r") as file:
    foods = json.load(file)


def random_food():
    meal_list = []
    for food in foods:
        meal_list.append(food["name"])

    random_meal = random.choice(meal_list)
    return random_meal


def init_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def start_game():
        index = date.today().toordinal() % len(foods)
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

        return render_template(
            "index.html", clues=[clues[0]], message="", guessed=False
        )

    @app.route("/guess", methods=["GET", "POST"])
    def make_guess():
        guess = request.form.get("guess").strip().lower()
        answer = session.get("answer")
        clues = session.get("clues", [])
        attempts = session.get("attempts", 1)
        guesses = session.get("guesses", [])

        if guess in guesses:
            flash("You have already guessed that food. Try again!")
            return render_template(
                "index.html",
                clues=clues[:attempts],
                guesses=reversed(guesses),
                guessed=False,
            )

        # Add guess to previous guesses list and increase attempts by 1
        guesses.append(guess)
        session["guesses"] = guesses
        attempts += 1
        session["attempts"] = attempts

        # End the game if the guess is correct or if attempts exceed 5
        if guess == answer:
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

    @app.route("/correct", methods=["GET"])
    def correct_guess():
        answer = session.get("answer")
        attempts = session.get("attempts")
        return render_template("correct.html", answer=answer, attempts=attempts)

    @app.route("/incorrect", methods=["GET"])
    def incorrect_guess():
        answer = session.get("answer")
        attempts = session.get("attempts")

        return render_template("incorrect.html", answer=answer, attempts=attempts)
