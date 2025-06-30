from flask import Flask, render_template, request, session
from flask import redirect, url_for
import json
import random
from datetime import date

with open('data/foods.json', 'r') as file:
    foods = json.load(file)
    
def random_food():
    meal_list = []
    for food in foods:
            meal_list.append(food['name'])
    
    random_meal = random.choice(meal_list)
    return random_meal


def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def start_game():
        index = date.today().toordinal() % len(foods)
        food = foods[index]
        
        clues = [
            food['clue1'],
            food['clue2'],
            food['clue3'],
            food['clue4'],
            food['clue5']
        ]
        
        # store state in session
        session['answer'] = food['name']
        session['clues'] = clues
        session['attempts'] = 0
        session['guesses'] = []
        
        return render_template('index.html', clue1=clues[0], message="", guessed=False)
    
    @app.route('/guess', methods = ['GET', 'POST'])
    def make_guess():
        guess = request.form.get('guess').strip().lower() 
        answer = session.get('answer')
        clues = session.get('clues', [])
        attempts = session.get('attempts', 0)
        guesses = session.get('guesses', [])
        
        if guess == answer:
            return render_template('index.html', clue1="", message="Congratulations! You guessed it right!", guesses=guesses, guessed=True)
        
        attempts += 1
        guesses.append(guess)
        session['attempts'] = attempts
        session['guesses'] = guesses

        if attempts == 5:
            return render_template('index.html', clue="", message=f"You are out the guesses. The answer was: {answer}", guesses=guesses, guessed=True)
        elif attempts == 1:
            return render_template('index.html', clue1=clues[0], clue2=clues[1], message="Try again!", guesses=guesses, guessed=False)
        elif attempts == 2:
            return render_template('index.html', clue1=clues[0], clue2=clues[1], clue3=clues[2], message="Try again!", guesses=guesses, guessed=False)
        elif attempts == 3:
            return render_template('index.html', clue1=clues[0], clue2=clues[1], clue3=clues[2], clue4=clues[3], message="Try again!", guesses=guesses, guessed=False)
        else: 
            return render_template('index.html', clue1=clues[0], clue2=clues[1], clue3=clues[2], clue4=clues[3], clue5=clues[4], message="Try again!", guesses=guesses, guessed=False)
    
