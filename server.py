from flask import Flask, render_template, request

my_flask_app = Flask(__name__)


@my_flask_app.route('/')
def index():
    return render_template('index.html')


@my_flask_app.route('/new/')
def all_news():
    return render_template('new_card.html')


@my_flask_app.route('/cards/')
def all_cards():
    return render_template('all_cards.html')


@my_flask_app.route('/training/')
def training():
    return render_template('training.html')       


if __name__ == "__main__":
    my_flask_app.run(debug=True)   